---
type: topic
domain: backend
stage: 1
section: "1.1"
order: 3
status: todo
level: junior
notion_id: 3ea33104867981e388abd527913e239a
tags: [domain/backend, stage/1, topic/networks, topic/security, level/junior, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# TLS, сертификаты, mTLS

↑ [[BE 1.1 Сети и протоколы для бэкенда|1.1 Сети и протоколы для бэкенда]] · ← [[BE 1.1.2 HTTP для бэкенда — методы, статусы, заголовки, keep-alive, HTTP-2 и HTTP-3|Предыдущая]] · → [[BE 1.1.4 DNS, балансировка, reverse proxy|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Бэкендер настраивает HTTPS в Kestrel и nginx, доверие к внутренним сертификатам между сервисами, mTLS для межсервисного общения. Ошибки вида «The SSL connection could not be established» надо уметь диагностировать.

## Подтемы
- [ ] Что даёт TLS
- [ ] Сертификаты X.509, цепочка доверия, форматы
- [ ] Handshake TLS 1.3, forward secrecy
- [ ] Где терминировать TLS
- [ ] mTLS
- [ ] TLS в ASP.NET Core и .NET
- [ ] Диагностика

## Объяснение

### Что даёт TLS
Конфиденциальность (шифрование), целостность (данные не подменены), аутентичность сервера (сертификат), а при mTLS — и клиента.

### Сертификаты и цепочка доверия
- Сертификат X.509 содержит: домен (CN и SAN), публичный ключ, срок действия, издателя, подпись CA.
- Цепочка: **leaf** (сертификат сайта) → **intermediate CA** → **root CA** (в доверенном хранилище ОС).
- Клиент проверяет: подписи по цепочке, срок, совпадение домена с SAN, отзыв (OCSP, CRL).
- Приватный ключ хранится только на сервере (`.key`, `.pfx` с паролем).

Форматы: PEM (`.crt`, `.pem`, `.key` — base64), PFX/PKCS#12 (`.pfx` — сертификат и ключ в одном файле), DER (бинарный).

### Handshake TLS 1.3 (коротко)
ClientHello (шифры, key share, SNI — имя хоста) → ServerHello + сертификат + key share → общий симметричный ключ через (EC)DHE → зашифрованный трафик. 1 RTT, при возобновлении 0-RTT.

**Forward secrecy:** эфемерные ключи DH. Даже утечка приватного ключа сервера не позволит расшифровать записанный ранее трафик.

### Где терминировать TLS
- **На nginx или балансировщике** (TLS termination): внутри сети — HTTP. Проще управление сертификатами. Типично для docker-compose-инфраструктуры.
- **End-to-end:** TLS до самого сервиса (требования безопасности, zero trust).
- **Re-encryption:** nginx расшифровывает и снова шифрует до бэкенда.

### mTLS (mutual TLS)
Клиент тоже предъявляет сертификат, сервер проверяет его по доверенному CA. Используют для межсервисной аутентификации (часто это делает service mesh: Istio, Linkerd).

## ASP.NET Core и .NET
```csharp
// Kestrel с сертификатом из файла
builder.WebHost.ConfigureKestrel(k => k.ListenAnyIP(443, o =>
    o.UseHttps("/certs/service.pfx", builder.Configuration["Cert:Password"])));

// HSTS и редирект на HTTPS (если TLS не терминируется на прокси)
app.UseHsts();
app.UseHttpsRedirection();
```
```csharp
// mTLS: требовать клиентский сертификат
builder.WebHost.ConfigureKestrel(k => k.ConfigureHttpsDefaults(h =>
    h.ClientCertificateMode = ClientCertificateMode.RequireCertificate));
builder.Services.AddAuthentication(CertificateAuthenticationDefaults.AuthenticationScheme).AddCertificate();

// HttpClient с клиентским сертификатом
builder.Services.AddHttpClient("secure").ConfigurePrimaryHttpMessageHandler(() =>
{
    var handler = new HttpClientHandler();
    handler.ClientCertificates.Add(X509CertificateLoader.LoadPkcs12FromFile("client.pfx", password));
    return handler;
});
```
Dev-сертификат: `dotnet dev-certs https --trust`. В контейнерах внутренний CA добавляют в образ (`update-ca-certificates`).

## Нюансы и подводные камни
- **Никогда** не отключайте проверку сертификата в проде (`ServerCertificateCustomValidationCallback = (_, _, _, _) => true`). Для внутренних CA — добавить CA в доверенные.
- Истёкший сертификат — классический ночной инцидент. Нужны автообновление (certbot, cert-manager) и алерты на срок.
- Несовпадение домена и SAN (обращение по IP или внутреннему имени) → ошибка валидации.
- Внутри Docker-сети сервисы обращаются по именам контейнеров: сертификат должен содержать эти имена, либо TLS терминируется снаружи.
- Keycloak за прокси: неправильный `hostname` или proto даёт ошибки токенов из-за http и https в `iss`.

## Диагностика
```bash
openssl s_client -connect api.example.com:443 -servername api.example.com   # цепочка и сертификат
curl -v https://api.example.com/health                                        # детали handshake
openssl x509 -in cert.pem -noout -dates -subject -ext subjectAltName          # сроки и SAN
```

## Вопросы с ответами
> [!question]- Как клиент проверяет сертификат сервера?
> Строит цепочку до доверенного корневого CA, проверяет подписи, срок действия, совпадение имени хоста с SAN и статус отзыва.

> [!question]- Что такое mTLS и когда его применяют?
> Взаимная аутентификация: клиент тоже предъявляет сертификат. Используют для межсервисной связи, B2B-интеграций и zero-trust сетей.

> [!question]- Где лучше терминировать TLS?
> Обычно на обратном прокси или балансировщике: централизованное управление сертификатами, меньше нагрузки на сервисы. Если требования безопасности строже — end-to-end или re-encryption до сервисов.

> [!question]- Что такое forward secrecy?
> Свойство, при котором утечка долгосрочного приватного ключа не позволяет расшифровать прошлые сессии, потому что ключи сессий получены через эфемерный Diffie–Hellman.

## Связанные темы
- Предыдущая: [[N:3ea331048679812882d9f5e746fcd550]] · Следующая: [[N:3ea331048679817aa584c01ff29564d5]]
- TLS глазами браузера: [[N:3ea3310486798116a40fe7fca0db88e4]]
- TLS в проде (certbot, HSTS): [[N:3ea33104867981c28785ddea2bf2dc4f]]
- Криптография в .NET: [[N:3ea331048679818080eee95e1cd52107]]
- Секреты: [[N:3ea331048679819c9bb7c741225859ca]]
