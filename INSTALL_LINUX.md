> Актуальная схема установки из GitHub Release описана в [RELEASE.md](RELEASE.md).

# 🐧 Установка PlayerokCardinal на Linux

Подробная инструкция по установке бота на Linux (Ubuntu/Debian)

---

## 📋 Требования

- Ubuntu 20.04+ или Debian 11+
- Доступ к `sudo`
- Минимум 1 ГБ свободного места

---

## 🚀 Быстрая установка

### Шаг 1: Скачайте установочный скрипт

```bash
wget -qO- https://raw.githubusercontent.com/bzzwwww/PlayerokCardinal/main/install-ubuntu.sh | sudo bash -s -- --repo bzzwwww/PlayerokCardinal --ref v1.1.3
```

Или с помощью `curl`:

```bash
curl -fsSL https://raw.githubusercontent.com/bzzwwww/PlayerokCardinal/main/install-ubuntu.sh | sudo bash -s -- --repo bzzwwww/PlayerokCardinal --ref v1.1.3
```

### Шаг 2: Сделайте скрипт исполняемым

Скрипт можно запускать сразу через pipe, отдельный `chmod +x` не нужен.

### Шаг 4: Следуйте инструкциям на экране

#### Скрипт установки спросит:
1. **Имя пользователя** для бота (например: `poc`, `cardinal`, `playerok`)

#### После установки запустится первичная настройка, которая спросит:
1. **Token Playerok** (JWT токен из Cookie браузера)
   - 📖 **[Как получить Token →](GET_TOKEN.md)**
   - Откройте playerok.com в браузере
   - Используйте расширение Cookie-Editor
   - Скопируйте значение cookie `token`
2. **User Agent** (можно пропустить Enter)
   - Узнать на https://whatmyuseragent.com
3. **Telegram Bot Token** (от @BotFather)
   - Подойдет любой корректный Telegram Bot Token
4. **Пароль для бота** (8+ символов, буквы + цифры)
5. **Прокси** (опционально, формат: `login:password@ip:port` или `ip:port`)

---

## 🎯 Что делает скрипт автоматически

✅ Устанавливает Python 3.11/3.12  
✅ Создаёт отдельного пользователя для бота  
✅ Настраивает виртуальное окружение  
✅ Устанавливает все зависимости  
✅ Создаёт systemd service  
✅ Настраивает кодировку  
✅ Запускает первичную настройку

---

## 🎮 Управление ботом

После установки бот запустится как фоновый процесс (systemd service).

### Основные команды:

```bash
# Остановить бота
sudo systemctl stop PlayerokCardinal@username

# Запустить бота
sudo systemctl start PlayerokCardinal@username

# Перезапустить бота
sudo systemctl restart PlayerokCardinal@username

# Посмотреть статус и логи
sudo systemctl status PlayerokCardinal@username -n100

# Добавить в автозагрузку
sudo systemctl enable PlayerokCardinal@username

# Убрать из автозагрузки
sudo systemctl disable PlayerokCardinal@username
```

**⚠️ Замените `username` на имя, которое вы указали при установке!**

---

## 📂 Где находятся файлы

```
/home/username/
├── PlayerokCardinal/        # Основная папка бота
│   ├── configs/            # Конфигурационные файлы
│   ├── logs/               # Логи
│   ├── storage/            # Хранилище данных
│   └── plugins/            # Плагины
└── pyvenv/                 # Виртуальное окружение Python
```

---

## 📝 Просмотр логов

### В реальном времени:

```bash
sudo journalctl -u PlayerokCardinal@username -f
```

### Последние 100 строк:

```bash
sudo systemctl status PlayerokCardinal@username -n100
```

### Файл логов:

```bash
cat /home/username/PlayerokCardinal/logs/log.log
```

---

## ⚙️ Ручная установка (альтернатива)

Если автоматический скрипт не подходит:

### 1. Установите Python 3.11

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-dev python3.11-venv
```

### 2. Создайте пользователя

```bash
sudo useradd -m poc
```

### 3. Скачайте бота

```bash
sudo -u poc git clone https://github.com/bzzwwww/PlayerokCardinal.git /home/poc/PlayerokCardinal
```

### 4. Создайте виртуальное окружение

```bash
sudo -u poc python3.11 -m venv /home/poc/pyvenv
```

### 5. Установите зависимости

```bash
sudo -u poc /home/poc/pyvenv/bin/pip install -U pip
sudo -u poc /home/poc/pyvenv/bin/pip install -r /home/poc/PlayerokCardinal/requirements.txt
```

### 6. Настройте systemd service

```bash
sudo ln -sf /home/poc/PlayerokCardinal/PlayerokCardinal@.service /etc/systemd/system/PlayerokCardinal@.service
sudo systemctl daemon-reload
```

### 7. Первый запуск

```bash
sudo -u poc /home/poc/pyvenv/bin/python /home/poc/PlayerokCardinal/main.py
```

Заполните данные, затем запустите как service:

```bash
sudo systemctl start PlayerokCardinal@poc
```

---

## 🔧 Редактирование конфигов

```bash
# Основной конфиг
sudo nano /home/username/PlayerokCardinal/configs/_main.cfg

# Автоответчик
sudo nano /home/username/PlayerokCardinal/configs/auto_response.cfg

# Автовыдача
sudo nano /home/username/PlayerokCardinal/configs/auto_delivery.cfg
```

После изменений перезапустите бота:

```bash
sudo systemctl restart PlayerokCardinal@username
```

---

## 🔄 Обновление бота

```bash
# Остановите бота
sudo systemctl stop PlayerokCardinal@username

# Перейдите в папку
cd /home/username/PlayerokCardinal

# Обновите код
sudo -u username git pull

# Обновите зависимости
sudo -u username /home/username/pyvenv/bin/pip install -U -r requirements.txt

# Запустите бота
sudo systemctl start PlayerokCardinal@username
```

---

## ❌ Удаление бота

```bash
# Остановите и отключите service
sudo systemctl stop PlayerokCardinal@username
sudo systemctl disable PlayerokCardinal@username

# Удалите файлы
sudo rm /etc/systemd/system/PlayerokCardinal@.service
sudo systemctl daemon-reload
sudo userdel -r username  # Удалит пользователя и его файлы
```

---

## 🐛 Решение проблем

### Бот не запускается

```bash
# Проверьте статус
sudo systemctl status PlayerokCardinal@username

# Проверьте логи
sudo journalctl -u PlayerokCardinal@username -n50
```

### Ошибка с Python

```bash
# Проверьте версию Python
python3.11 --version

# Переустановите зависимости
sudo -u username /home/username/pyvenv/bin/pip install -U -r /home/username/PlayerokCardinal/requirements.txt
```

### Ошибка "Permission denied"

```bash
# Проверьте владельца файлов
ls -la /home/username/PlayerokCardinal

# Восстановите права
sudo chown -R username:username /home/username/PlayerokCardinal
sudo chown -R username:username /home/username/pyvenv
```

### Порт уже используется

```bash
# Проверьте запущенные процессы
ps aux | grep python

# Убейте зависший процесс
sudo kill -9 <PID>
```

---

## 📞 Поддержка

- **GitHub**: [bzzwwww/PlayerokCardinal](https://github.com/bzzwwww/PlayerokCardinal)
- **Telegram**: [@bzzwwww](https://t.me/bzzwwww)
- **Issues**: [Сообщить о проблеме](https://github.com/bzzwwww/PlayerokCardinal/issues)

---

## 💡 Полезные советы

✅ Используйте уникальный пароль для Telegram бота  
✅ Регулярно делайте бэкап папки `configs`  
✅ Не запускайте бота от root  
✅ Добавьте в автозагрузку после проверки работы  
✅ Следите за логами первые дни работы

---

## 🎉 Готово!

Теперь ваш бот работает 24/7 на Linux сервере!

Напишите `/start` вашему Telegram боту для управления.
