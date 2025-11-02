# Software Example

File-based application for batch processing Telegram sessions.

## Architecture

```
software_example/
├── main.py             # Entry point
├── process.py          # Core processing logic
├── loader.py           # Session file loader
├── config.py           # Configuration
├── handlers.py         # Error handlers
└── logging_config.py   # Logging setup
```

## Features

- File-based session management
- Batch processing with queue
- Automatic proxy rotation
- JSON attachment support
- Dead session auto-cleanup
- Interactive file management

## Directory Structure

```
examples/data/
├── proxies.txt
└── sessions/
    ├── alive/          # Active sessions (session + json pairs)
    ├── dead/           # Dead sessions (auto-moved)
    └── wrong/          # Invalid files
```

## Configuration

Edit `config.py` or use environment variables:

```bash
export API_ID=12345
export API_HASH=your_hash
export PROXY_TYPE=socks5
export SLEEP_INTERVAL=1
export CONNECTION_RETRIES=0
```

## Usage

```bash
python main.py
```

## File Format

Each account requires two files:

**session.session** - Telethon session file

**session.json** - Account metadata:
```json
{
  "api_id": 12345,
  "api_hash": "your_hash",
  "phone": "+1234567890",
  "device_model": "iPhone 14 Pro",
  "system_version": "iOS 16.0"
}
```

## Flow

1. Load proxies from file
2. Scan session directory
3. Load all session+json pairs
4. Add clients to processing queue
5. For each client:
   - Set proxy
   - Connect and authorize
   - Process account
   - Remove from queue
6. Move dead sessions to dead folder
7. Continue until queue is empty

## Error Handling

- **Dead errors**: Session moved to `dead/` folder
- **Connection errors**: Proxy marked as failed, retry later
- **Other errors**: Logged and processing continues

## Interactive Features

- Auto-detect unpaired files
- Option to create missing JSON files
- Option to move invalid files
- User-friendly console prompts

## Use Cases

- Batch account verification
- Session health check
- Account data collection
- Automated account operations
- Session organization

