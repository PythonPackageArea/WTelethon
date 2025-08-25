# Telethon Patch Lite

Расширенная версия Telethon с дополнительными возможностями для работы с Telegram API.

## Возможности

### 🔐 Аутентификация
- **QR-авторизация** - вход через QR-код
- **SMS-авторизация** - классический вход по номеру телефона
- **Веб-авторизация** - авторизация для веб-приложений
- **Регистрация** - создание новых аккаунтов

### 👤 Управление аккаунтом
- **Информация пользователя** - загрузка данных профиля
- **Двухфакторная авторизация** - работа с 2FA
- **Проверка спамбота** - детекция блокировок
- **Premium статус** - проверка подписки
- **Уведомления** - регистрация устройств

### 📎 Система вложений
- **JsonAttachment** - хранение данных в JSON файлах
- **MemoryAttachment** - управление данными в памяти
- **PlatformAttachment** - эмуляция различных платформ

### 🔧 Дополнительные инструменты
- **Прокси** - поддержка SOCKS прокси
- **Обработка исключений** - расширенная система ошибок
- **Конвертация сессий** - преобразование между форматами
- **Файловые операции** - работа с вложениями

## Установка

```bash
pip install git+https://github.com/PythonPackageArea/WTelethon.git
```

## Быстрый старт

```python
import asyncio
from telethon_patch import TelegramClient, JsonAttachment, MemoryAttachment

async def main():
    # Создание клиента с JSON вложением
    json_attachment = await JsonAttachment("account.json").load()
    
    client = TelegramClient(
        "account.session",
        json_attachment=json_attachment
    )
    
    await client.connect()
    
    # Проверка авторизации
    if await client.check_authorization():
        print("Авторизован")
        
        # Загрузка информации о пользователе
        await client.load_me_info()
        print(f"Пользователь: {client.memory.first_name}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Примеры использования

### Работа с вложениями

```python
# Memory attachment
memory = MemoryAttachment(
    api_id=12345,
    api_hash="your_api_hash"
)

# JSON attachment
json_data = JsonAttachment("data.json")
await json_data.load()

# Заполнение памяти из JSON
json_data.fill_memory(memory)
```

### Проверка статуса аккаунта

```python
# Проверка Premium
premium_until = await client.load_premium_info()
if premium_until:
    print(f"Premium до {premium_until}")

# Проверка спамбота
is_blocked = await client.check_spambot()
if is_blocked:
    print("Аккаунт заблокирован спамботом")

# Двухфакторная авторизация
await client.check_twofa("password123")
```

## Структура проекта

```
telethon_patch/
├── attachments/          # Система вложений
│   ├── json/            # JSON вложения
│   ├── memory/          # Память клиента
│   └── platform/        # Платформенные данные
├── tools/               # Инструменты
│   ├── client/          # Клиентские инструменты
│   │   ├── auth/        # Авторизация
│   │   └── account/     # Управление аккаунтом
│   ├── attachments/     # Работа с вложениями
│   └── storages/        # Хранилища данных
├── patches/             # Патчи для Telethon
└── storages/            # Системы хранения
```

## Зависимости

- `telethon` - базовая библиотека
- `pydantic` - валидация данных
- `aiofile` - асинхронная работа с файлами
- `python_socks[asyncio]` - поддержка SOCKS прокси
- `phonenumbers` - работа с номерами телефонов
- `loguru` - логирование

## Лицензия

MIT License
