# 🧩 Гайд по созданию плагинов для Playerok Cardinal

Этот гайд поможет вам создать свой плагин для Playerok Cardinal (POC).

## 📋 Содержание

- [Структура плагина](#-структура-плагина)
- [Обязательные поля](#-обязательные-поля)
- [Обработчики событий](#-обработчики-событий)
- [Пример простого плагина](#-пример-простого-плагина)
- [Продвинутые возможности](#-продвинутые-возможности)
- [Публикация плагина](#-публикация-плагина)

## 📁 Структура плагина

Плагин для Playerok Cardinal - это обычный Python файл (`.py`), который должен быть размещён в папке `plugins/`.

### Минимальная структура:

```python
# Обязательные константы
NAME = "Название плагина"
VERSION = "1.0.0"
DESCRIPTION = "Описание плагина"
CREDITS = "@ВашTelegram"
UUID = "ваш-uuid-здесь"
SETTINGS_PAGE = False  # True, если есть страница настроек
BIND_TO_DELETE = None  # Функция, вызываемая при удалении плагина

# Обработчики событий (опционально)
BIND_TO_PRE_INIT = []
BIND_TO_POST_INIT = []
BIND_TO_PRE_START = []
BIND_TO_POST_START = []
BIND_TO_PRE_STOP = []
BIND_TO_POST_STOP = []
BIND_TO_NEW_MESSAGE = []
BIND_TO_NEW_ORDER = []
BIND_TO_CHAT_INITIALIZED = []
BIND_TO_NEW_DEAL = []
BIND_TO_ITEM_PAID = []
BIND_TO_ITEM_SENT = []
BIND_TO_DEAL_CONFIRMED = []
```

## 🔧 Обязательные поля

| Поле | Тип | Описание |
|------|-----|----------|
| `NAME` | `str` | Название плагина (отображается в списке плагинов) |
| `VERSION` | `str` | Версия плагина (например, "1.0.0") |
| `DESCRIPTION` | `str` | Описание функционала плагина |
| `CREDITS` | `str` | Автор плагина (например, "@bzzwwww") |
| `UUID` | `str` | Уникальный идентификатор плагина (формат UUID v4) |
| `SETTINGS_PAGE` | `bool` | Есть ли у плагина страница настроек в Telegram |
| `BIND_TO_DELETE` | `Callable \| None` | Функция, вызываемая при удалении плагина |

### Генерация UUID

Для генерации UUID используйте один из способов:

**Python:**
```python
import uuid
UUID = str(uuid.uuid4())
```

**Онлайн генератор:**
- https://www.uuidgenerator.net/
- https://www.uuid.org/

⚠️ **Важно:** UUID должен быть уникальным для каждого плагина!

## 🎯 Обработчики событий

Обработчики событий - это функции, которые вызываются при определённых событиях в работе бота.

### Доступные обработчики:

| Обработчик | Когда вызывается | Аргументы |
|-----------|------------------|-----------|
| `BIND_TO_PRE_INIT` | Перед инициализацией Cardinal | `Cardinal` |
| `BIND_TO_POST_INIT` | После инициализации Cardinal | `Cardinal` |
| `BIND_TO_PRE_START` | Перед запуском Cardinal | `Cardinal` |
| `BIND_TO_POST_START` | После запуска Cardinal | `Cardinal` |
| `BIND_TO_PRE_STOP` | Перед остановкой Cardinal | `Cardinal` |
| `BIND_TO_POST_STOP` | После остановки Cardinal | `Cardinal` |
| `BIND_TO_NEW_MESSAGE` | Новое сообщение в чате | `Cardinal`, `Message` |
| `BIND_TO_NEW_ORDER` | Новый заказ | `Cardinal`, `Order` |
| `BIND_TO_CHAT_INITIALIZED` | Чат инициализирован | `Cardinal`, `Chat` |
| `BIND_TO_NEW_DEAL` | Новая сделка | `Cardinal`, `Deal` |
| `BIND_TO_ITEM_PAID` | Товар оплачен | `Cardinal`, `Item` |
| `BIND_TO_ITEM_SENT` | Товар отправлен | `Cardinal`, `Item` |
| `BIND_TO_DEAL_CONFIRMED` | Сделка подтверждена | `Cardinal`, `Deal` |

### Пример обработчика:

```python
def on_new_message(cardinal, message):
    """
    Обработчик нового сообщения.
    
    :param cardinal: Экземпляр Cardinal
    :param message: Объект сообщения
    """
    # Ваш код здесь
    print(f"Получено новое сообщение: {message.text}")

BIND_TO_NEW_MESSAGE = [on_new_message]
```

## 📝 Пример простого плагина

Вот пример простого плагина, который логирует все новые сообщения:

```python
import uuid
from Utils.logger import get_logger

# Обязательные константы
NAME = "Message Logger"
VERSION = "1.0.0"
DESCRIPTION = "Логирует все новые сообщения в чатах"
CREDITS = "@bzzwwww"
UUID = str(uuid.uuid4())  # Сгенерируйте свой UUID!
SETTINGS_PAGE = False
BIND_TO_DELETE = None

# Логгер
logger = get_logger("plugin.message_logger")

def on_new_message(cardinal, message):
    """
    Обработчик нового сообщения.
    """
    try:
        logger.info(f"Новое сообщение в чате {message.chat.id}: {message.text}")
    except Exception as e:
        logger.error(f"Ошибка в плагине {NAME}: {e}")

# Регистрируем обработчик
BIND_TO_NEW_MESSAGE = [on_new_message]
```

## 🚀 Продвинутые возможности

### 1. Добавление команд в Telegram бот

Вы можете добавить свои команды в меню Telegram бота:

```python
def on_post_init(cardinal):
    """
    Вызывается после инициализации Cardinal.
    """
    # Добавляем команды в меню бота
    cardinal.add_telegram_commands(
        UUID,
        [
            ("my_command", "Описание команды", True),  # True = добавить в меню
            ("another_command", "Другая команда", False),  # False = не добавлять в меню
        ]
    )

BIND_TO_POST_INIT = [on_post_init]
```

### 2. Обработка команд Telegram

Для обработки команд Telegram вам нужно использовать обработчики из `tg_bot`:

```python
from tg_bot.bot import TGBot
from telebot import types

def on_post_init(cardinal):
    """
    Регистрируем обработчик команды.
    """
    if cardinal.telegram:
        @cardinal.telegram.bot.message_handler(commands=["my_command"])
        def handle_my_command(message: types.Message):
            cardinal.telegram.bot.send_message(
                message.chat.id,
                "Привет! Это команда из плагина!"
            )

BIND_TO_POST_INIT = [on_post_init]
```

### 3. Страница настроек плагина

Если вы хотите добавить страницу настроек для плагина:

```python
SETTINGS_PAGE = True

def on_post_init(cardinal):
    """
    Регистрируем страницу настроек.
    """
    # Ваш код для создания страницы настроек
    pass

BIND_TO_POST_INIT = [on_post_init]
```

### 4. Очистка при удалении плагина

Если плагин создаёт файлы или использует ресурсы, которые нужно очистить:

```python
import os

def cleanup_on_delete():
    """
    Функция вызывается при удалении плагина.
    """
    # Удаляем созданные файлы
    if os.path.exists("plugins/my_plugin_data.json"):
        os.remove("plugins/my_plugin_data.json")
    
    print(f"Плагин {NAME} удалён, данные очищены")

BIND_TO_DELETE = cleanup_on_delete
```

### 5. Использование конфигурации

Вы можете сохранять настройки плагина в отдельный файл:

```python
import json
import os

CONFIG_FILE = "plugins/my_plugin_config.json"

def load_config():
    """Загружает конфигурацию плагина."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"setting1": "default_value"}

def save_config(config):
    """Сохраняет конфигурацию плагина."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def on_post_init(cardinal):
    """Загружаем конфигурацию при инициализации."""
    config = load_config()
    print(f"Настройка плагина: {config['setting1']}")

BIND_TO_POST_INIT = [on_post_init]
```

## 📤 Публикация плагина

### Подготовка к публикации

1. **Проверьте код:**
   - Убедитесь, что все обязательные поля заполнены
   - UUID должен быть уникальным
   - Проверьте, что плагин не содержит ошибок

2. **Добавьте комментарии:**
   - Опишите функционал плагина
   - Укажите автора и контакты
   - Добавьте инструкции по использованию

3. **Протестируйте:**
   - Установите плагин в тестовый экземпляр POC
   - Проверьте все функции плагина
   - Убедитесь, что плагин корректно удаляется

### Публикация на GitHub

1. Создайте репозиторий для вашего плагина
2. Добавьте файл `README.md` с описанием
3. Укажите совместимость с версиями Playerok Cardinal
4. Добавьте примеры использования

### Пример README для плагина:

```markdown
# My Plugin

Плагин для Playerok Cardinal, который делает что-то полезное.

## Установка

1. Скачайте файл `my_plugin.py`
2. Поместите его в папку `plugins/` вашего бота
3. Перезапустите бота командой `/restart`

## Настройка

Плагин работает из коробки, но вы можете настроить его через...

## Совместимость

- Playerok Cardinal v1.0.0+

## Автор

@YourTelegram
```

## ⚠️ Важные замечания

1. **Безопасность:**
   - Не устанавливайте плагины из непроверенных источников
   - Плагины имеют полный доступ к системе бота
   - Проверяйте код плагинов перед установкой

2. **Производительность:**
   - Не блокируйте основной поток выполнения
   - Используйте асинхронные операции для долгих задач
   - Обрабатывайте исключения в своих обработчиках

3. **Совместимость:**
   - Указывайте минимальную версию Playerok Cardinal
   - Тестируйте плагин на разных версиях
   - Обновляйте плагин при изменении API

## 📚 Полезные ссылки

- **Документация PlayerokAPI**: Изучите `PlayerokAPI/` для работы с API Playerok
- **Примеры плагинов**: Посмотрите на существующие плагины в сообществе
- **Telegram канал**: [@bzwwplugins_bot](https://t.me/bzwwplugins_bot) - канал с плагинами
- **Чат поддержки**: [@bzwwplugins_bot](https://t.me/bzwwplugins_bot)

## 💡 Примеры использования

### Пример 1: Автоответ на определённые сообщения

```python
import uuid

NAME = "Auto Reply"
VERSION = "1.0.0"
DESCRIPTION = "Автоматически отвечает на определённые сообщения"
CREDITS = "@bzzwwww"
UUID = str(uuid.uuid4())
SETTINGS_PAGE = False
BIND_TO_DELETE = None

def on_new_message(cardinal, message):
    """Отвечаем на сообщение 'привет'."""
    if message.text and "привет" in message.text.lower():
        cardinal.account.send_message(
            message.chat.id,
            "Привет! Чем могу помочь?"
        )

BIND_TO_NEW_MESSAGE = [on_new_message]
```

### Пример 2: Уведомления о новых сделках

```python
import uuid
from Utils.logger import get_logger

NAME = "Deal Notifier"
VERSION = "1.0.0"
DESCRIPTION = "Отправляет уведомления о новых сделках в Telegram"
CREDITS = "@bzzwwww"
UUID = str(uuid.uuid4())
SETTINGS_PAGE = False
BIND_TO_DELETE = None

logger = get_logger("plugin.deal_notifier")

def on_new_deal(cardinal, deal):
    """Отправляем уведомление о новой сделке."""
    if cardinal.telegram:
        message = f"💰 Новая сделка!\n\nID: {deal.id}\nСумма: {deal.price} RUB"
        for user_id in cardinal.telegram.authorized_users:
            try:
                cardinal.telegram.bot.send_message(user_id, message)
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления: {e}")

BIND_TO_NEW_DEAL = [on_new_deal]
```

---

**Удачи в создании плагинов! 🚀**

Если у вас есть вопросы, обращайтесь в [Telegram](https://t.me/bzwwplugins_bot).

