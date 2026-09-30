---
type: topic
domain: devops
stage: 5
order: 4
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Service, Ingress, DNS внутри кластера

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Сетевые абстракции Kubernetes — одна из главных тем: как поды находят друг друга и как трафик попадает снаружи.

## Проблема

IP подов эфемерны. **Service** — стабильная точка доступа (виртуальный IP + DNS-имя) и балансировка между подами, выбранными по **селектору меток** (только Ready поды).

## Типы Service

| Тип | Доступ | Применение |
|---|---|---|
| **ClusterIP** (по умолчанию) | внутри кластера (виртуальный IP) | общение между сервисами |
| **NodePort** | порт 30000–32767 на каждой ноде | тесты, bare metal, база для LB |
| **LoadBalancer** | внешний балансировщик облака (или MetalLB) | прямой внешний доступ к сервису (L4) |
| **ExternalName** | DNS CNAME на внешнее имя | обращение к внешним сервисам по внутреннему имени |
| **Headless** (`clusterIP: None`) | DNS возвращает IP подов (без VIP) | StatefulSet, клиентская балансировка, gRPC |

```yaml
apiVersion: v1
kind: Service
metadata: { name: api }
spec:
  selector: { app: api }
  ports:
    - name: http
      port: 80            # порт сервиса
      targetPort: 8080    # порт контейнера (число или имя порта)
  type: ClusterIP
  sessionAffinity: None   # ClientIP при необходимости
```

Механизм: контроллер EndpointSlice формирует список IP:port готовых подов; **kube-proxy** (iptables/IPVS) перенаправляет трафик с ClusterIP на один из них (DNAT). Service без селектора + ручные Endpoints — для внешних систем.

## DNS внутри кластера

**CoreDNS** создаёт записи:

- `<service>.<namespace>.svc.cluster.local` → ClusterIP;
- в том же namespace достаточно короткого имени `api`; между namespaces: `api.clinic` или `api.clinic.svc`;
- **headless**: A-записи всех подов; у StatefulSet — `pod-0.service.ns.svc.cluster.local`;
- SRV-записи для именованных портов;
- переменные окружения `API_SERVICE_HOST`, `API_SERVICE_PORT` (устаревший способ, внедряются при старте пода).

Поды получают `/etc/resolv.conf` с `search <ns>.svc.cluster.local svc.cluster.local cluster.local` и `ndots:5`: короткие имена дополняются; внешние имена порождают несколько лишних запросов (оптимизация: FQDN с точкой `example.com.`, `dnsConfig`, NodeLocal DNSCache).

```bash
kubectl run -it --rm dns --image=busybox:1.36 -- nslookup api.clinic.svc.cluster.local
kubectl get endpoints api; kubectl get endpointslices -l kubernetes.io/service-name=api
```

## Ingress

**Ingress** — L7-правила маршрутизации внешнего HTTP(S) трафика на Services; реализуется **Ingress-контроллером** (NGINX, Traefik, HAProxy, Envoy/Contour, cloud LB). Один внешний IP обслуживает много хостов/путей, терминирует TLS.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: clinic
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "20m"
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  ingressClassName: nginx
  tls:
    - hosts: [app.example.com]
      secretName: app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - { path: /api,  pathType: Prefix, backend: { service: { name: api, port: { number: 80 } } } }
          - { path: /,     pathType: Prefix, backend: { service: { name: web, port: { number: 80 } } } }
```

`pathType`: `Exact`, `Prefix`, `ImplementationSpecific`. Настройки зависят от контроллера (аннотации).

**Gateway API** — современная замена Ingress: разделение ролей (`GatewayClass` → `Gateway` → `HTTPRoute`/`GRPCRoute`/`TCPRoute`), богатая маршрутизация (веса, заголовки, зеркалирование), стандартизированные функции без аннотаций.

## Внешний доступ: схемы

```text
Клиент → DNS → LoadBalancer (облачный L4, один IP) → Ingress Controller (поды nginx) → Service → Pods
```

- **LoadBalancer** на каждый сервис дорог; Ingress — один LB на много сервисов;
- bare metal: **MetalLB** (L2/BGP) даёт IP для LoadBalancer; `hostNetwork`/NodePort + внешний LB;
- **externalTrafficPolicy**: `Cluster` (по умолчанию, SNAT, равномерно, теряется IP клиента) или `Local` (сохраняет IP клиента, только локальные поды);
- `X-Forwarded-For` / PROXY protocol для реального IP;
- gRPC/WebSocket — аннотации/настройки контроллера, L7-балансировка.

## Session affinity и балансировка

Service распределяет **соединения** (kube-proxy, не запросы): долгие HTTP/2/gRPC-соединения «прилипают» к одному поду → L7-балансировка (Envoy/Linkerd) или headless + клиентская балансировка. `sessionAffinity: ClientIP` — привязка по IP; cookie-affinity — на Ingress.

## Диагностика

| Симптом | Проверка |
|---|---|
| Service недоступен | `kubectl get endpoints` пуст → селектор не совпадает с метками подов / поды не Ready |
| Connection refused | `targetPort` не тот; приложение слушает `127.0.0.1` |
| Работает по IP пода, не по имени | DNS (CoreDNS, `ndots`, namespace) |
| Ingress 404/503 | нет правила/host, backend без endpoints, неверный `ingressClassName` |
| 502 от Ingress | поды не отвечают, протокол (HTTPS backend), таймауты |
| Снаружи недоступен LoadBalancer | security group/firewall, `EXTERNAL-IP <pending>` (нет облачного провайдера/MetalLB) |
| Теряется IP клиента | `externalTrafficPolicy: Cluster`, L4 без PROXY protocol |

```bash
kubectl port-forward svc/api 8080:80           # обход Ingress
kubectl exec -it debug -- curl -v http://api.clinic.svc:80/health
kubectl describe ingress clinic; kubectl logs -n ingress-nginx deploy/ingress-nginx-controller
```

## Вопросы с ответами

> [!question]- Чем ClusterIP отличается от NodePort и LoadBalancer?
> ClusterIP доступен только внутри кластера; NodePort открывает порт на всех нодах; LoadBalancer создаёт внешний балансировщик (обычно поверх NodePort) с внешним IP.

> [!question]- Зачем нужен Ingress, если есть LoadBalancer?
> Ingress — L7-маршрутизация (хосты, пути, TLS) нескольких сервисов через один внешний IP; LoadBalancer на каждый сервис дорог и не умеет маршрутизировать по HTTP.

> [!question]- Service есть, но запросы не доходят. Что проверите первым?
> `kubectl get endpoints <svc>`: есть ли адреса (совпадают ли селектор и метки подов, готовы ли поды), затем `targetPort` и доступность из другого пода.
