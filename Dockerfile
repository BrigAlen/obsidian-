# Всё приложение в одном образе: сайт (Quartz) + API (ASP.NET Core).
# Сборка из корня репозитория: docker build -t vault .

# 1. Сайт
FROM node:22-bookworm-slim AS site
RUN apt-get update && apt-get install -y --no-install-recommends git python3 perl rsync ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . /src/vault
ARG BASE_URL=localhost
RUN bash /src/vault/site/build.sh /src/vault /src/quartz /src/public "$BASE_URL"

# 2. API
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS api
WORKDIR /src
COPY api/src/VaultApi/VaultApi.csproj .
RUN dotnet restore
COPY api/src/VaultApi/ .
RUN dotnet publish -c Release -o /out --no-restore

# 3. Итоговый образ
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=api /out .
COPY --from=site /src/public ./wwwroot
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "VaultApi.dll"]
