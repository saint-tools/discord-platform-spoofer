# Discord Platform Spoofer

A lightweight Python tool that connects a single Discord account across multiple spoofed platform identities simultaneously — desktop, web, iOS, Android, Xbox, PlayStation, and VR — and monitors active session data via `SESSIONS_REPLACE` events.

## Features

- Spoof multiple Discord client platforms at the same time
- Configurable platform list via `config.json`
- Live session monitoring through raw WebSocket events

## Supported Platforms

| Key | Platform |
|---|---|
| `desktop` | Windows Desktop Client |
| `web` | Discord Web (Chrome) |
| `ios` | Discord iOS (iPhone) |
| `android` | Discord Android (Pixel) |
| `xbox` | Xbox Series X |
| `playstation` | PlayStation 5 |
| `vr` | Discord VR Headset |

## Requirements

- Python 3.10+
- `discord.py`

Install dependencies:

```bash
pip install discord.py-self
```

## Configuration

Edit `config.json` before running:

```json
{
  "token": "YOUR_TOKEN_HERE",
  "active_platforms": ["desktop", "web", "ios", "android", "xbox", "playstation", "vr"]
}
```

- **`token`** — Your Discord user token.
- **`active_platforms`** — List of platforms to spoof. Remove any you don't want active.

> ⚠️ **Never share your token publicly or commit it to a public repository.**

## Usage

```bash
python spoof.py
```

Each platform client will log when it's ready and print active session clients whenever a `SESSIONS_REPLACE` event is received.

Example output:

```
[DESKTOP] Ready as YourUser#0000
[IOS] Ready as YourUser#0000
[DESKTOP] SESSIONS_REPLACE, active clients: ['desktop', 'ios', 'web']
```

## Project Structure

```
.
├── spoof.py        # Main script
├── config.json     # Token and platform configuration
└── README.md
```

## Disclaimer

This project is for **educational and research purposes only**. Using self-bots or modifying client identification may violate [Discord's Terms of Service](https://discord.com/terms). Use at your own risk.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
