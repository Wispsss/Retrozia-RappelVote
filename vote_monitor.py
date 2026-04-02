"""
Retrozia Vote Monitor
Login → JWT token → polling API → notification ntfy
"""

import asyncio
import os
from datetime import datetime, timedelta

import aiohttp
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("RETROZIA_USERNAME")
PASSWORD = os.getenv("RETROZIA_PASSWORD")
NTFY_URL = f"https://ntfy.sh/{os.getenv('NTFY_TOPIC')}"
LOGIN_URL = "https://retrozia.fun/api/auth/login"
API_URL = f"https://retrozia.fun/api/auth/profile?login={USERNAME}"
RECHECK_AFTER_NOTIF = 5 * 60


def now():
    return datetime.now().strftime("%H:%M:%S")


async def login(session: aiohttp.ClientSession) -> str:
    payload = {"login": USERNAME, "password": PASSWORD}
    async with session.post(LOGIN_URL, json=payload) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise RuntimeError(f"Login échoué ({resp.status}) : {body}")
        data = await resp.json()
        print(f"[{now()}] ✅ Connecté — token JWT obtenu")
        return data["token"]


async def send_ntfy(title: str, message: str):
    headers = {"Title": title, "Priority": "high", "Tags": "ballot_box_with_check"}
    async with aiohttp.ClientSession() as s:
        async with s.post(NTFY_URL, data=message.encode("utf-8"), headers=headers) as resp:
            status = "✅" if resp.status == 200 else f"❌ (http {resp.status})"
            print(f"[{now()}] {status} Notif : {title}")


async def fetch_profile(session: aiohttp.ClientSession):
    try:
        async with session.get(API_URL) as resp:
            if resp.status == 401:
                print(f"[{now()}] 🔄 Token expiré, re-login...")
                return None, True
            if resp.status != 200:
                print(f"[{now()}] ❌ API error : {resp.status}")
                return None, False
            data = await resp.json()
            return data.get("profile"), False
    except Exception as e:
        print(f"[{now()}] ❌ Exception : {e}")
        return None, False


async def main():
    print(f"[{now()}] 🚀 Démarrage du monitor Retrozia Vote")

    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        token = await login(session)
        session.headers.update({"Authorization": f"Bearer {token}"})

        while True:
            profile, need_relogin = await fetch_profile(session)

            if need_relogin:
                token = await login(session)
                session.headers.update({"Authorization": f"Bearer {token}"})
                continue

            if profile is None:
                print(f"[{now()}] ⚠️ Retry dans 60s...")
                await asyncio.sleep(60)
                continue

            total = profile.get("totalVotes", "?")

            if profile.get("canVoteNow", False):
                print(f"[{now()}] 🗳️ Vote disponible ! (total : {total})")
                await send_ntfy(
                    "🗳️ Vote Retrozia disponible !",
                    f"Tu peux voter maintenant sur retrozia.fun\nTotal votes : {total}",
                )
                print(f"[{now()}] ⏰ Revérif dans {RECHECK_AFTER_NOTIF // 60} min...")
                await asyncio.sleep(RECHECK_AFTER_NOTIF)
            else:
                seconds = profile.get("secondsUntilNextVote", 0)
                vote_time = (datetime.now() + timedelta(seconds=seconds)).strftime("%H:%M:%S")
                print(f"[{now()}] ⏳ Vote dans {seconds}s — disponible à {vote_time}")
                print(f"[{now()}] 💤 Attente de {seconds}s...")
                await asyncio.sleep(seconds)


if __name__ == "__main__":
    asyncio.run(main())
