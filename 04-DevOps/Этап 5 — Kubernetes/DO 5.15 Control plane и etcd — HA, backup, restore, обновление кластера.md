---
type: topic
domain: devops
stage: 5
order: 15
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Control plane и etcd: HA, backup, restore, обновление кластера

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Для senior/self-managed: как устроена отказоустойчивость control plane, etcd, бэкапы и обновление.

## Высокая доступность control plane

**Stacked etcd**: на каждом control-plane узле — apiserver, scheduler, controller-manager **и** etcd (проще, но потеря узла = потеря и API, и члена etcd). **External etcd**: отдельный кластер etcd (больше узлов, изоляция).

Рекомендуется **3 control-plane узла** (в разных зонах), перед ними **балансировщик** (kube-vip, HAProxy+keepalived, облачный LB) с единым адресом API (`controlPlaneEndpoint`).

- **apiserver** — stateless, работает активно-активно за LB;
- **scheduler и controller-manager** — **leader election** (один активен, остальные в standby);
- **etcd** — кворум Raft.

## etcd

Распределённое хранилище ключ–значение (Raft), содержит **всё состояние** кластера. Потеря etcd без бэкапа = потеря кластера (объекты, но не данные приложений на томах).

### Кворум

| Узлов | Кворум | Допустимых отказов |
|---|---|---|
| 1 | 1 | 0 |
| 3 | 2 | 1 |
| 5 | 3 | 2 |
| 4 | 3 | 1 (чётное число не даёт выигрыша) |

Используйте **нечётное число** (3 или 5). Потеря кворума → кластер только для чтения (объекты не меняются, работающие поды продолжают работать, но нет планирования/самовосстановления).

### Производительность и эксплуатация

- **быстрые диски (SSD/NVMe)** и низкая задержка `fsync` (`etcd_disk_wal_fsync_duration_seconds` p99 < 10 мс), отдельный диск;
- стабильная сеть между членами (`etcd_network_peer_round_trip_time_seconds`);
- размер БД ограничен (по умолчанию 2 ГБ, `--quota-backend-bytes`, рекомендованно до 8 ГБ): следить, **compaction** и **defrag**;
- не хранить в etcd большие объёмы (ConfigMap/Secret до ~1 МБ, лишние Events);
- шифрование Secret at rest (`EncryptionConfiguration`), mTLS между членами, ограничить доступ к порту 2379/2380;
- мониторинг: `etcd_server_has_leader`, `etcd_server_leader_changes_seen_total`, `etcd_mvcc_db_total_size_in_bytes`, апдейты, latency apiserver.

```bash
export ETCDCTL_API=3
ETCDCTL="etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key"
$ETCDCTL endpoint health --cluster; $ETCDCTL endpoint status --cluster -w table; $ETCDCTL member list -w table
$ETCDCTL alarm list
$ETCDCTL defrag --cluster
```

## Backup etcd

```bash
$ETCDCTL snapshot save /backup/etcd-$(date +%F_%H%M).db
etcdutl snapshot status /backup/etcd-2026-09-30_0300.db -w table     # проверка целостности (hash, ревизия, размер)
```

Практики: **регулярно (каждые 15–60 минут, зависит от RPO)**, хранить вне кластера (S3/MinIO, шифрование, Object Lock), ротация, **автоматически** (CronJob на control-plane, Velero не заменяет etcd-бэкап, а дополняет), **периодически проверять восстановление**. Управляемые кластеры — бэкапит провайдер, но ресурсы/тома всё равно защищают Velero + GitOps.

## Restore etcd

Одиночный/потеря кворума:

```bash
# 1. остановить apiserver и etcd (на kubeadm: убрать манифесты static pods из /etc/kubernetes/manifests)
etcdutl snapshot restore /backup/etcd-2026-09-30_0300.db --data-dir /var/lib/etcd-restored \
   --name cp1 --initial-cluster cp1=https://10.0.0.11:2380,cp2=...,cp3=... --initial-advertise-peer-urls https://10.0.0.11:2380
# 2. указать новый data-dir в манифесте etcd, вернуть манифесты, дождаться кворума
# 3. для multi-node: восстановить на ВСЕХ членах из одного снапшота с общим --initial-cluster-token
```

После восстановления: состояние = на момент снапшота (созданные позже объекты исчезнут, а удалённые вернутся), проверить фактические ресурсы, PV и рабочие нагрузки, перевыпустить токены/сертификаты при необходимости; **тренировать** на стенде. Потеря одного члена из 3: удалить (`member remove`) и добавить заново (`member add`), а не полностью восстанавливать.

## Обновление кластера (kubeadm)

```bash
# control plane (по одному узлу)
apt-mark unhold kubeadm && apt install -y kubeadm=1.31.2-1.1 && apt-mark hold kubeadm
kubeadm upgrade plan
sudo kubeadm upgrade apply v1.31.2            # на первом узле; на остальных: kubeadm upgrade node
kubectl drain cp1 --ignore-daemonsets
apt install -y kubelet=1.31.2-1.1 kubectl=1.31.2-1.1 && systemctl restart kubelet
kubectl uncordon cp1
# воркеры: drain → kubeadm upgrade node → обновить kubelet → uncordon (по одному/пачками, учитывая PDB)
```

Контрольный список: **бэкап etcd**; совместимость версий компонентов (CNI, CSI, ingress, operators, cert-manager, Helm-чарты); удалённые API (`kubent`, `pluto`); тест на staging; окно и план отката (откат minor-обновления сложен: часто восстановление из бэкапа); мониторинг во время обновления; обновление по порядку: apiserver → controller-manager/scheduler → kubelet/kube-proxy → аддоны.

Управляемые решения: обновление через консоль/API; surge-ноды, **blue/green пулов**; Cluster API, kOps, Talos (`talosctl upgrade-k8s`).

## Сертификаты

kubeadm выпускает сертификаты на **1 год** (кроме CA на 10 лет): `kubeadm certs check-expiration`, `kubeadm certs renew all` (или авто-продление при `kubeadm upgrade`); kubelet может ротировать клиентские (`rotateCertificates`) и серверные сертификаты; алерты на срок (например, `apiserver_client_certificate_expiration_seconds`, x509-exporter). Истёкший сертификат = недоступность кластера.

## Безопасность control plane

- приватный endpoint API, ограничение по IP, **аудит-логи** (`--audit-policy-file`), admission-контроллеры (PodSecurity, NodeRestriction), отключить анонимный доступ, RBAC;
- kubelet: `--authorization-mode=Webhook`, `--anonymous-auth=false`, закрытый порт 10250;
- шифрование секретов в etcd (KMS), ограничение доступа к etcd и бэкапам;
- защита `/etc/kubernetes` и `admin.conf`;
- CIS Benchmark: `kube-bench`;
- регулярные обновления (CVE).

## Отказы и поведение

| Событие | Эффект |
|---|---|
| Потеряли 1 из 3 control-plane | кластер работает, перевыборы, нужна замена узла |
| Потеряли кворум etcd | API доступен только для чтения/недоступен, нагрузки продолжают работать, нет новых планирований и самовосстановления |
| Недоступен apiserver | запущенные поды работают (kubelet кэширует), нет управления и обновлений |
| Отказал leader scheduler/controller-manager | leader election, секунды |
| Отказ воркера | поды пересоздаются на других нодах (`node-monitor-grace-period` ~40 с + `tolerationSeconds` 300 с по умолчанию для NoExecute) |

## Managed против self-managed

Управляемый control plane (EKS/GKE/AKS/Yandex) снимает заботу об etcd, обновлениях и HA; self-managed — контроль и сложность. Для большинства команд — managed.

## Вопросы с ответами

> [!question]- Почему для etcd используют нечётное число узлов?
> Кворум — большинство; при 3 узлах допускается 1 отказ, при 4 — также 1, поэтому чётный узел лишь увеличивает стоимость и риск без выигрыша в отказоустойчивости.

> [!question]- Что произойдёт с запущенными приложениями при потере кворума etcd?
> Уже работающие поды продолжат работать, но изменения API невозможны: нет новых развёртываний, масштабирования, планирования и самовосстановления, пока кворум не восстановят.

> [!question]- Как организовать бэкап и восстановление etcd?
> Регулярные снапшоты `etcdctl snapshot save`, хранение вне кластера, проверка целостности и регулярные учения по восстановлению (`etcdutl snapshot restore` на всех членах); дополнительно Velero и GitOps.
