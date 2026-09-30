---
type: topic
domain: devops
stage: 5
order: 5
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# Ingress-контроллеры, cert-manager и TLS в кластере

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Ingress без контроллера — просто объект. Нужно знать популярные контроллеры и автоматизацию сертификатов.

## Ingress-контроллеры

| Контроллер | Особенности |
|---|---|
| **ingress-nginx** (Kubernetes community) | самый распространённый, аннотации `nginx.ingress.kubernetes.io/*`, ConfigMap для глобальных настроек |
| **NGINX Inc. Ingress** | коммерческий вариант + VirtualServer CRD |
| **Traefik** | динамическая конфигурация, CRD IngressRoute, встроенный ACME, middleware |
| **HAProxy Ingress** | высокая производительность |
| **Contour / Envoy Gateway / Emissary** | на базе Envoy, Gateway API |
| **Istio Gateway, Cilium Gateway** | интеграция с service mesh/eBPF |
| **Облачные** (AWS ALB controller, GCE, Azure AGIC) | используют L7 LB облака |

Установка (пример): `helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace --set controller.replicaCount=2`. Контроллер — Deployment/DaemonSet + Service типа LoadBalancer (или NodePort/hostNetwork на bare metal).

`IngressClass` (`ingressClassName: nginx`) связывает Ingress с контроллером; можно запускать несколько контроллеров (внутренний и внешний).

## Настройка ingress-nginx

Аннотации на Ingress:

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"         # HTTPS | GRPC | GRPCS
    nginx.ingress.kubernetes.io/rewrite-target: /$2              # с regex path
    nginx.ingress.kubernetes.io/limit-rps: "20"
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8"
    nginx.ingress.kubernetes.io/affinity: cookie
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
    nginx.ingress.kubernetes.io/auth-url: "http://oauth2-proxy.auth.svc/oauth2/auth"
```

Глобальные параметры — ConfigMap (`use-forwarded-headers`, `enable-real-ip`, `proxy-buffer-size`, `log-format-upstream`, `hsts`). Кастомные сниппеты (`configuration-snippet`) отключены по умолчанию из-за риска безопасности.

Диагностика: `kubectl logs -n ingress-nginx deploy/ingress-nginx-controller`, `kubectl exec ... -- cat /etc/nginx/nginx.conf`, плагин `kubectl ingress-nginx`.

## TLS в кластере

Сертификат хранится в **Secret типа `kubernetes.io/tls`** (`tls.crt`, `tls.key`); Ingress ссылается через `tls.secretName`. Вручную — неудобно: нужна автоматизация выпуска и продления.

## cert-manager

Оператор, который автоматически выпускает и продлевает сертификаты (Let's Encrypt/ACME, Vault, внутренний CA, Venafi) и хранит их в Secret.

Установка: `helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set crds.enabled=true`.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: letsencrypt }
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ops@example.com
    privateKeySecretRef: { name: letsencrypt-account-key }
    solvers:
      - http01: { ingress: { ingressClassName: nginx } }
      - dns01:                                              # для wildcard
          cloudflare: { apiTokenSecretRef: { name: cf-token, key: api-token } }
        selector: { dnsZones: ["example.com"] }
```

Использование — аннотация на Ingress (`cert-manager.io/cluster-issuer: letsencrypt`) + `tls:` секция: cert-manager создаст `Certificate`, пройдёт challenge и запишет Secret. Или явный ресурс:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: { name: app-tls, namespace: clinic }
spec:
  secretName: app-tls
  dnsNames: [app.example.com]
  issuerRef: { name: letsencrypt, kind: ClusterIssuer }
  duration: 2160h
  renewBefore: 720h
```

Проверка: `kubectl get certificate,certificaterequest,order,challenge -A`, `kubectl describe certificate`, логи cert-manager. Тесты — staging ACME (`acme-staging-v02`), чтобы не упереться в лимиты.

**Внутренний PKI**: `Issuer` типа `CA`/`Vault`/`SelfSigned` для сервис-сервис TLS (mTLS); `csi-driver` для сертификатов в подах; `trust-manager` распространяет CA-bundle.

## Gateway API

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: { name: public, namespace: infra }
spec:
  gatewayClassName: nginx
  listeners:
    - { name: https, port: 443, protocol: HTTPS, hostname: "*.example.com",
        tls: { mode: Terminate, certificateRefs: [{ name: wildcard-tls }] },
        allowedRoutes: { namespaces: { from: All } } }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: api, namespace: clinic }
spec:
  parentRefs: [{ name: public, namespace: infra }]
  hostnames: [app.example.com]
  rules:
    - matches: [{ path: { type: PathPrefix, value: /api } }]
      backendRefs: [{ name: api, port: 80, weight: 90 }, { name: api-canary, port: 80, weight: 10 }]
```

Преимущества: разделение ответственности (платформа владеет Gateway, команды — Route), стандартные веса/заголовки/зеркалирование, типизированные поля вместо аннотаций. cert-manager интегрируется с Gateway.

## Надёжность ingress-слоя

- **минимум 2 реплики** контроллера, `podAntiAffinity`, `PodDisruptionBudget`, HPA;
- ресурсы и лимиты, `topologySpreadConstraints`;
- `externalTrafficPolicy: Local` и PROXY protocol для реального IP;
- мониторинг (метрики Prometheus: запросы, статусы, латентность, ошибки конфигурации), алерты на срок сертификатов;
- **обновления контроллера**: совместимость аннотаций, canary-обновление;
- разделение **внешнего и внутреннего** ingress; защита админ-путей; WAF (ModSecurity в ingress-nginx, `enable-modsecurity`);
- **лимиты безопасности**: запрет произвольных snippet-аннотаций, ограничения namespace.

## Типичные проблемы

| Симптом | Причина |
|---|---|
| Ingress не получает адрес | нет контроллера/LoadBalancer, неверный `ingressClassName` |
| Сертификат не выпускается | challenge не проходит (порт 80, DNS, аннотации, лимиты), `Order pending` |
| 308/redirect loop | TLS terminates на LB и ingress снова редиректит: `use-forwarded-headers`, `ssl-redirect` |
| Неверный сертификат (Fake Certificate) | нет `tls`/Secret не создан: используется дефолтный self-signed |
| 413 | `proxy-body-size` |
| Не видит реальный IP | `externalTrafficPolicy`, `use-forwarded-headers`, PROXY protocol |

## Вопросы с ответами

> [!question]- Что делает cert-manager?
> Автоматически выпускает и продлевает TLS-сертификаты (ACME/Let's Encrypt, Vault, внутренний CA) для ресурсов Ingress/Gateway и хранит их в Secret.

> [!question]- Чем Gateway API лучше Ingress?
> Разделяет роли (инфраструктурный Gateway и прикладные Route), поддерживает веса, заголовки, зеркалирование и другие протоколы стандартными полями без контроллер-специфичных аннотаций.

> [!question]- Как сделать ingress-слой отказоустойчивым?
> Несколько реплик с anti-affinity по зонам, PDB, HPA, выделенные ноды при необходимости, мониторинг и корректный externalTrafficPolicy.
