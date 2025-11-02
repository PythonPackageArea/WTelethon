# WTelethon Examples

Professional examples demonstrating all features of the WTelethon library.

## Quick Start

Each example file is standalone and interactive. Run any example:

```bash
python 01_basic_client.py
```

## Important Note

**TelegramClient requires either `memory_attachment` or `json_attachment`** - it does NOT accept `api_id` and `api_hash` directly.

```python
# CORRECT
memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
client = TelegramClient("session.session", memory_attachment=memory)

# INCORRECT
client = TelegramClient("session.session", api_id=12345, api_hash="your_hash")  # This will NOT work
```

## Example Files

### 01_basic_client.py
Client initialization with different session types and configurations.

**Features:**
- Simple SQLite session client with MemoryAttachment
- Memory session (no file storage)
- String session (portable format)
- Auth key hex format
- Memory attachment configuration
- Proxy setup

**Use cases:**
- First-time client setup
- Session format conversion
- Custom device/platform configuration

---

### 02_authentication.py
All authentication methods supported by Telegram.

**Features:**
- QR code authentication
- Web authorization
- SMS code authentication (automatic)
- SMS code authentication (manual)

**Use cases:**
- Adding new accounts
- Re-authorizing existing sessions
- Multi-device authorization

---

### 03_account_management.py
Account status checking and management.

**Features:**
- Authorization validation
- User info loading
- Spambot status check
- 2FA verification
- 2FA password change

**Use cases:**
- Account health monitoring
- Profile data collection
- Security management
- Ban detection

---

### 04_session_conversion.py
Session format conversion utilities.

**Features:**
- Extract session string
- Get auth key hex
- Convert memory to SQLite
- Load SQLite to memory
- Auth key to SQLite conversion

**Use cases:**
- Session backup
- Format migration
- Cross-platform compatibility

---

### 05_tdata_operations.py
TData format operations (Telegram Desktop).

**Features:**
- Create TData from single session
- Create TData from multiple sessions
- Extract TData information
- Convert TData to sessions

**Use cases:**
- Telegram Desktop integration
- Multi-account management
- Session export/import

---

### 06_proxy_management.py
Proxy configuration and rotation.

**Features:**
- Direct proxy setup
- Load proxies from file via `helpers.storages.proxies.load_proxies_from_file()`
- Storage-based proxy selection
- Random proxy rotation
- Error handling and failover
- Current proxy inspection

**Use cases:**
- Anonymous connections
- Geographic restrictions bypass
- Connection reliability
- Load distribution

---

### 07_attachments.py
JSON and Memory attachments for data management.

**Features:**
- JSON attachment loading
- JSON attachment creation
- Memory attachment usage
- Update JSON from memory
- Helper methods
- Combined attachments

**Use cases:**
- Persistent account data
- Configuration management
- Runtime data manipulation
- Data synchronization

---

### 08_complete_workflow.py
Real-world complete workflows.

**Features:**
- Complete account check
- Batch session conversion
- Multi-account TData creator
- Account health monitor

**Use cases:**
- Production account management
- Bulk operations
- Automated monitoring
- Session maintenance

---

### 09_exception_handling.py
Error handling and recovery.

**Features:**
- Dead error detection
- Flood wait handling
- Session password (2FA) errors
- Phone number ban detection
- Custom error handlers
- Common error patterns

**Use cases:**
- Robust error handling
- Session validation
- Recovery strategies
- Production reliability

---

### 10_advanced_features.py
Advanced functionality and integrations.

**Features:**
- Periodic task scheduling
- Platform data customization
- Dynamic platform updates
- Notification registration
- File globbing utilities
- Multiple client management
- Logging configuration

**Use cases:**
- Background monitoring
- Device emulation
- Push notifications
- Batch processing
- Debug and logging

---

## Data Structure

```
examples/
├── 01_basic_client.py
├── 02_authentication.py
├── 03_account_management.py
├── 04_session_conversion.py
├── 05_tdata_operations.py
├── 06_proxy_management.py
├── 07_attachments.py
├── 08_complete_workflow.py
├── 09_exception_handling.py
├── 10_advanced_features.py
├── data/
│   ├── proxies.txt
│   ├── account.json
│   └── sessions/
│       ├── alive/
│       ├── dead/
│       └── converted/
└── README.md
```

## Configuration

### API Credentials

All examples require MemoryAttachment or JsonAttachment with credentials:

```python
from wtelethon import MemoryAttachment

memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
```

Get your credentials from https://my.telegram.org

### Proxy Format

File format for `proxies.txt`:

```
host:port:username:password
1.2.3.4:1080:user:pass
5.6.7.8:1080
```

### JSON Attachment Format

Example `account.json` structure:

```json
{
  "api_id": 12345,
  "api_hash": "your_hash",
  "phone": "+1234567890",
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe",
  "device_model": "iPhone 14 Pro",
  "system_version": "iOS 16.0",
  "app_version": "9.5.0",
  "lang_code": "en",
  "system_lang_code": "en-US",
  "twofa": "secret_password"
}
```

## Common Patterns

### Basic Client Setup

```python
import asyncio
from wtelethon import TelegramClient, MemoryAttachment

async def main():
    memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
    client = TelegramClient("session.session", memory_attachment=memory)
    await client.connect()

    if await client.is_user_authorized():
        print("Authorized")

    await client.disconnect()

asyncio.run(main())
```

### With JSON Attachment

```python
from wtelethon import TelegramClient, JsonAttachment

json_attach = JsonAttachment("account.json")
await json_attach.load()

client = TelegramClient("session.session", json_attachment=json_attach)
await client.connect()
```

### With Proxy

```python
from wtelethon import TelegramClient, MemoryAttachment, helpers

await helpers.storages.proxies.load_proxies_from_file("proxies.txt", "socks5")

memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
client = TelegramClient("session.session", memory_attachment=memory)
client.set_proxy_from_storage()
await client.connect()
```

### Error Handling

```python
from wtelethon import TelegramClient, MemoryAttachment, utils

memory = MemoryAttachment(api_id=12345, api_hash="your_hash")
client = TelegramClient("session.session", memory_attachment=memory)
await client.connect()

try:
    await client.check_authorization(provoke_error=True)
except Exception as exc:
    if utils.is_dead_error(exc):
        print("Session is dead")
```

## Requirements

```bash
pip install wtelethon
```

Optional for TData support:

```bash
pip install cryptg
```

## Notes

- All examples are interactive and menu-driven
- File paths are relative to the examples directory
- Sessions are stored in SQLite format by default
- TData operations require the `cryptg` package
- Proxy support includes SOCKS5 and HTTP types
- All examples follow async/await patterns
- **TelegramClient always requires memory_attachment or json_attachment**

## Support

For issues and questions:
- GitHub Issues: https://github.com/PythonPackageArea/WTelethon
- Documentation: See project README
