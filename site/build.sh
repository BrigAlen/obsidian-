#!/bin/bash
# Сборка сайта (Quartz) для Docker-образа: то же, что шаг «Assemble site sources» в deploy.yml.
# Использование: site/build.sh <каталог vault> <каталог для Quartz> <каталог результата> [baseUrl]
set -euo pipefail
VAULT="$1"; Q="$2"; OUT="$3"; BASE="${4:-localhost}"

[ -d "$Q/.git" ] || git clone --depth 1 --branch v4 https://github.com/jackyzha0/quartz.git "$Q"
rm -rf "$Q/content"; mkdir "$Q/content"
rsync -a --exclude '.git' --exclude '.github' --exclude 'site' --exclude '_templates' --exclude 'api' \
      --exclude 'README.md' --exclude 'Dockerfile' --exclude 'render.yaml' --exclude '.dockerignore' "$VAULT/" "$Q/content/"
cp "$VAULT/site/quartz.config.ts" "$Q/quartz.config.ts"
sed -i "s|baseUrl: \"[^\"]*\"|baseUrl: \"$BASE\"|" "$Q/quartz.config.ts"
find "$Q/content" -name '*.md' -exec perl -0pi -e 's/```dataview.*?```\n//gs' {} +
python3 "$VAULT/site/meta.py" "$Q/content"
python3 "$VAULT/site/resolve_links.py" "$Q/content"
python3 "$VAULT/site/slugify.py" "$Q/content"
python3 "$VAULT/site/make_index.py" "$Q/content"
sed -i 's|slug.endsWith("/index") \|\| ||' "$Q/quartz/plugins/emitters/contentPage.tsx"
cp "$VAULT/site/quartz.layout.ts" "$Q/quartz.layout.ts"
cat "$VAULT/site/custom.scss" "$VAULT"/.obsidian/snippets/*.css > "$Q/quartz/styles/custom.scss"
[ -d "$VAULT/site/static" ] && cp -r "$VAULT/site/static/." "$Q/quartz/static/"

(cd "$Q" && npm ci --no-audit --no-fund && npx quartz build -o "$OUT")

# Подключаем клиентский код аккаунтов на каждую страницу
cp "$VAULT"/site/app/app.js "$VAULT"/site/app/app.css "$OUT/"
find "$OUT" -name '*.html' -exec sed -i 's|</head>|<link rel="stylesheet" href="/app.css"><script defer src="/app.js"></script></head>|' {} +
