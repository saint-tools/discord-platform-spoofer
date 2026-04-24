import discord
from discord.gateway import DiscordWebSocket
import json
import asyncio
import zlib
import contextvars
import json

PLATFORM_CONFIGS = {
    "desktop": {
        "os": "Windows",
        "browser": "Discord Client",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "browser_version": "124.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
    },
    "web": {
        "os": "Windows",
        "browser": "Discord Web",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "browser_version": "124.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
    },
    "ios": {
        "os": "iOS",
        "browser": "Discord iOS",
        "device": "iPhone16,2",
        "system_locale": "en-US",
        "browser_user_agent": "Discord/268.0 CFNetwork/1474 Darwin/23.0.0",
        "browser_version": "268.0",
        "os_version": "17.4.1",
        "referrer": "",
        "referring_domain": "",
    },
    "android": {
        "os": "Android",
        "browser": "Discord Android",
        "device": "Pixel 8",
        "system_locale": "en-US",
        "browser_user_agent": "Discord-Android/214116;ROM:13;Device:Pixel 8",
        "browser_version": "214.116",
        "os_version": "13",
        "referrer": "",
        "referring_domain": "",
    },
    "xbox": {
        "os": "Console",
        "browser": "Discord Embedded",
        "device": "Xbox Series X",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
        "browser_version": "",
        "os_version": "",
        "referrer": "",
        "referring_domain": "",
    },
    "playstation": {
        "os": "Console",
        "browser": "Discord Embedded",
        "device": "PlayStation 5",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (PlayStation 5 3.11) AppleWebKit/605.1.15 (KHTML, like Gecko)",
        "browser_version": "",
        "os_version": "",
        "referrer": "",
        "referring_domain": "",
    },
    "vr": {
        "os": "Console",
        "browser": "Discord VR",
        "device": "VR-Headset",
        "system_locale": "en-US",
        "browser_user_agent": "DiscordVR/12.45",
        "browser_version": "23.7.91",
        "os_version": "10.0.45",
        "referrer": "",
        "referring_domain": "",
    },
}

with open("config.json") as f:
    config = json.load(f)

TOKEN = config["token"]
ACTIVE_PLATFORMS = config["active_platforms"]

_platform_ctx = contextvars.ContextVar("platform", default="vr")


async def _patched_identify(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "capabilities": 4093,
            "properties": PLATFORM_CONFIGS[_platform_ctx.get()],
            "compress": False,
            "client_state": {
                "guild_versions": {},
                "highest_last_message_id": "0",
                "read_state_version": 0,
                "user_guild_settings_version": -1,
                "user_settings_version": -1,
                "private_channels_version": "0",
                "api_code_version": 0,
            },
        },
    }
    await self.send(json.dumps(payload))


DiscordWebSocket.identify = _patched_identify


class PlatformClient(discord.Client):
    def __init__(self, platform_name, **kwargs):
        super().__init__(**kwargs)
        self.platform_name = platform_name
        self._zlib_buffer = bytearray()
        self._zlib_decompressor = zlib.decompressobj()

    async def on_ready(self):
        print(f"[{self.platform_name.upper()}] Ready as {self.user}")

    async def on_socket_raw_receive(self, msg):
        try:
            if isinstance(msg, bytes):
                self._zlib_buffer.extend(msg)
                if len(msg) < 4 or msg[-4:] != b"\x00\x00\xff\xff":
                    return
                msg = self._zlib_decompressor.decompress(self._zlib_buffer)
                self._zlib_buffer = bytearray()
                msg = msg.decode("utf-8")
            data = json.loads(msg)
        except Exception:
            self._zlib_buffer = bytearray()
            self._zlib_decompressor = zlib.decompressobj()
            return

        if data.get("t") == "SESSIONS_REPLACE":
            sessions = data.get("d", [])
            clients = [s.get("client_info", {}).get("client") for s in sessions]
            print(f"[{self.platform_name.upper()}] SESSIONS_REPLACE, active clients: {clients}")


async def main():
    tasks = []
    for platform in ACTIVE_PLATFORMS:
        ctx = contextvars.copy_context()
        ctx.run(_platform_ctx.set, platform)
        tasks.append(
            asyncio.get_event_loop().create_task(
                PlatformClient(platform).start(TOKEN),
                context=ctx,
            )
        )
    await asyncio.gather(*tasks)


asyncio.run(main())