# Release Guide

Этот проект подготовлен для чистой публикации на GitHub без пользовательских токенов, логов и кэша.

## Что входит в релиз

- `PlayerokCardinal-1.1.2-windows.zip`
- `PlayerokCardinal-1.1.2-linux.tar.gz`
- `install-ubuntu.sh` для установки через `wget`

## Установка

### Windows

1. Скачайте `PlayerokCardinal-1.1.2-windows.zip` из GitHub Release.
2. Распакуйте архив.
3. Запустите `Setup.bat`.
4. После установки зависимостей запустите `Start.bat`.

### Ubuntu

```bash
wget -qO- https://raw.githubusercontent.com/bzzwwww/PlayerokCardinal/main/install-ubuntu.sh | sudo bash -s -- --repo bzzwwww/PlayerokCardinal --ref v1.1.2
```

Дополнительно можно указать пользователя:

```bash
wget -qO- https://raw.githubusercontent.com/bzzwwww/PlayerokCardinal/main/install-ubuntu.sh | sudo bash -s -- --repo bzzwwww/PlayerokCardinal --ref v1.1.2 --user playerok
```

## Сборка релиза локально

```bash
python tools/build_release.py --github-repo bzzwwww/PlayerokCardinal --github-ref v1.1.2
```

Готовые архивы появятся в папке `dist`.

## GitHub Actions

В репозитории есть workflow `.github/workflows/release.yml`.

Он:

1. собирает чистые архивы;
2. прикладывает их к GitHub Release;
3. публикует артефакты в `dist`.
