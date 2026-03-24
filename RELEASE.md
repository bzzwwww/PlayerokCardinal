# Release Guide

Этот проект подготовлен для чистой публикации на GitHub без пользовательских токенов, логов и кэша.

## Что входит в релиз

- `PlayerokCardinal-__APP_VERSION__-windows.zip`
- `PlayerokCardinal-__APP_VERSION__-linux.tar.gz`
- `install-ubuntu.sh` для установки через `wget`

## Установка

### Windows

1. Скачайте `PlayerokCardinal-__APP_VERSION__-windows.zip` из GitHub Release.
2. Распакуйте архив.
3. Запустите `Setup.bat`.
4. После установки зависимостей запустите `Start.bat`.

### Ubuntu

```bash
wget -qO- https://raw.githubusercontent.com/__GITHUB_REPO__/__GITHUB_REF__/install-ubuntu.sh | sudo bash -s -- --repo __GITHUB_REPO__ --ref __GITHUB_REF__
```

Дополнительно можно указать пользователя:

```bash
wget -qO- https://raw.githubusercontent.com/__GITHUB_REPO__/__GITHUB_REF__/install-ubuntu.sh | sudo bash -s -- --repo __GITHUB_REPO__ --ref __GITHUB_REF__ --user playerok
```

## Сборка релиза локально

```bash
python tools/build_release.py --github-repo __GITHUB_REPO__ --github-ref __GITHUB_REF__
```

Готовые архивы появятся в папке `dist`.

## GitHub Actions

В репозитории есть workflow `.github/workflows/release.yml`.

Он:

1. собирает чистые архивы;
2. прикладывает их к GitHub Release;
3. публикует артефакты в `dist`.
