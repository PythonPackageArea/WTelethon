# Service Example

API-based service for processing Telegram sessions with continuous workflow.

## Architecture

```
service_example/
├── main.py             # Entry point
├── process.py          # Core processing logic
├── api_mock.py         # API mock (replace with real API)
├── proxy_loader.py     # Proxy loading from API
├── handlers.py         # Error handlers
└── logging_config.py   # Logging setup
```

## Features

- API-based session management
- Continuous processing loop
- Automatic proxy rotation
- Error handling and recovery
- Dead session detection
- Connection error retry

## Configuration

Replace `api_mock.py` with your real API implementation:

```python
class YourAPI:
    def get_session_data(self) -> Optional[SessionData]:
        # Fetch session from your API
        pass
    
    async def get_proxies(self) -> list[dict]:
        # Fetch proxies from your API
        pass
    
    async def update_session_data(self, slug: str, dead: bool = False) -> None:
        # Update session status in your API
        pass
```

## Usage

```bash
python main.py
```

## Flow

1. Load proxies from API
2. Start continuous processing loop
3. For each iteration:
   - Request session data from API
   - Create Telegram client
   - Set proxy
   - Process client (connect, authorize)
   - Handle errors (dead, connection, other)
   - Update API with results
4. Wait 1 second and repeat

## Error Handling

- **Dead errors**: Session marked as dead in API
- **Connection errors**: Proxy marked as failed, retry later
- **Other errors**: Logged and re-raised

## Logging

- Console output
- File output (`service.log`)
- Multiple log levels (INFO, DEBUG, WARNING, ERROR)

## Use Cases

- Telegram session management service
- Account health monitoring
- Automated account operations
- Large-scale session processing

