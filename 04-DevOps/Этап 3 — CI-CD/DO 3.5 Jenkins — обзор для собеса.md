---
type: topic
domain: devops
stage: 3
order: 5
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 6
---

# Jenkins: обзор для собеса

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Jenkins всё ещё встречается в enterprise; достаточно уверенно ориентироваться: Pipeline, агенты, плагины, минусы.

## Что такое Jenkins

Open-source сервер автоматизации на Java: «мастер» (controller) оркестрирует, **агенты** (nodes) выполняют. Огромная экосистема плагинов (~1800+). Самостоятельно хостится: вы отвечаете за обновления, бэкапы, безопасность, масштабирование.

## Jenkinsfile (Declarative Pipeline)

```groovy
pipeline {
  agent { docker { image 'mcr.microsoft.com/dotnet/sdk:9.0' } }
  options { timeout(time: 30, unit: 'MINUTES'); disableConcurrentBuilds(); buildDiscarder(logRotator(numToKeepStr: '20')) }
  environment { REGISTRY = 'registry.example.com'; IMAGE = "${REGISTRY}/clinic/api" }
  parameters { choice(name: 'ENV', choices: ['staging', 'prod'], description: 'Окружение') }

  stages {
    stage('Build') { steps { sh 'dotnet build -c Release' } }
    stage('Test') {
      steps { sh 'dotnet test --logger trx' }
      post { always { junit '**/*.trx' } }
    }
    stage('Image') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'registry', usernameVariable: 'U', passwordVariable: 'P')]) {
          sh '''
            echo "$P" | docker login -u "$U" --password-stdin $REGISTRY
            docker build -t $IMAGE:$GIT_COMMIT .
            docker push $IMAGE:$GIT_COMMIT
          '''
        }
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      input { message 'Выкатить в prod?'; ok 'Да'; submitter 'release-managers' }
      steps { sh "./deploy.sh ${params.ENV} ${GIT_COMMIT}" }
    }
  }
  post {
    failure { slackSend channel: '#ci', message: "Сборка упала: ${env.BUILD_URL}" }
    cleanup { cleanWs() }
  }
}
```

**Scripted Pipeline** — Groovy с `node { ... }`, гибкость без структуры; Declarative рекомендуется.

## Основные понятия

| Понятие | Описание |
|---|---|
| **Controller** | UI, планирование, хранение конфигурации (`JENKINS_HOME`) |
| **Agent / node** | исполнитель: постоянный или эфемерный (Docker, Kubernetes plugin) |
| **Pipeline**, **Stage**, **Step** | конвейер, стадии, шаги |
| **Multibranch Pipeline** | автоматически создаёт пайплайн на каждую ветку/PR по `Jenkinsfile` |
| **Shared Library** | общий код пайплайнов в отдельном репозитории (`@Library('ci-lib') _`) |
| **Credentials** | хранилище секретов (пароли, токены, SSH-ключи, сертификаты), маскирование в логах |
| **Plugins** | Git, Pipeline, Docker, Kubernetes, Blue Ocean, SonarQube, Credentials, Role Strategy |
| **Triggers** | SCM poll, webhook, cron (`cron('H 2 * * *')`), upstream |
| **Jenkins Configuration as Code (JCasC)** | конфигурация Jenkins в YAML |

Агенты в Kubernetes:

```groovy
agent { kubernetes { yaml '''
  apiVersion: v1
  kind: Pod
  spec:
    containers:
    - name: dotnet
      image: mcr.microsoft.com/dotnet/sdk:9.0
      command: [sleep]
      args: [infinity]
''' } }
```

## Плюсы и минусы

| Плюсы | Минусы |
|---|---|
| гибкость, плагины на всё | «ад плагинов»: совместимость, уязвимости, поддержка |
| зрелость, большое сообщество | устаревший UI, Groovy, отладка пайплайнов |
| on-premise, полный контроль | администрирование: обновления, бэкапы, масштабирование |
| Shared Libraries | конфигурация в UI (дрейф) без JCasC; разные подходы в разных командах |
| любые ОС/агенты | безопасность: много исторических уязвимостей |

## Практики

- **Pipeline as Code** (`Jenkinsfile` в репозитории), JCasC + плагины зафиксированы (plugins.txt), Jenkins в контейнере/на Kubernetes;
- **эфемерные агенты**, а не долгоживущие (чистота, безопасность);
- не запускать сборки на controller (`executors = 0`);
- **Credentials** и Vault, доступ по ролям (Role Strategy/Matrix), SSO (OIDC/LDAP);
- обновление LTS-версий, резервные копии `JENKINS_HOME`;
- Shared Library для стандартных шагов;
- `timeout`, `retry`, `cleanWs`, ротация старых сборок;
- мониторинг (Prometheus plugin).

## Jenkins и GitLab CI/GitHub Actions

Jenkins — если уже много legacy-пайплайнов, нужна строгая on-prem-инфраструктура, сложные оркестрации. Для новых проектов чаще выбирают встроенный CI платформы: меньше обслуживания, интеграция с MR/PR.

## Что сказать на собесе

- «Использовал для сборки и деплоя: Multibranch, Declarative Pipeline, Shared Library; агенты — Docker/K8s; секреты — Credentials/Vault»;
- «Сейчас предпочитаю GitLab CI: конфигурация рядом с кодом, нет отдельного сервера»;
- знание проблем: плагины, Groovy sandbox, безопасность скриптов.

## Вопросы с ответами

> [!question]- Чем Declarative Pipeline отличается от Scripted?
> Declarative — структурированный синтаксис (`pipeline { stages {...} }`) с валидацией и `post`-блоками; Scripted — произвольный Groovy в `node {}`: гибче, но сложнее и менее читаем.

> [!question]- Зачем эфемерные агенты?
> Чистая среда на каждую сборку (нет «грязных» состояний), масштабирование по требованию, лучшая безопасность; агенты создаются в Kubernetes/Docker и удаляются после задания.

> [!question]- Как организовать переиспользование кода пайплайнов?
> Jenkins Shared Library: общий репозиторий с шагами и шаблонами пайплайнов, подключаемый через `@Library`.
