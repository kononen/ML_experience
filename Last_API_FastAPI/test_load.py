# test_load.py

import asyncio
import random
import time
import json
import os

import aiohttp  # pip install aiohttp

# 1) Целевая точка
TARGET = "http://api-server-2.your.domain:8000"

# 2) Параметры
N_REQUESTS = 10
CONCURRENT  = 3
MAX_DELAY   = 20
TIMEOUT     = 60  # сек

# 3) payload.json
HERE = os.path.dirname(__file__)
with open(os.path.join(HERE, "payload.json"), encoding="utf-8") as f:
    PAYLOAD = json.load(f)

async def send_predict(session: aiohttp.ClientSession, idx: int):
    await asyncio.sleep(random.uniform(0, MAX_DELAY))
    try:
        async with session.post(f"{TARGET}/predict", json=PAYLOAD, timeout=TIMEOUT) as resp:
            print(f"[Запрос {idx:02d}] → {resp.status}")
    except Exception as e:
        print(f"[Запрос {idx:02d}] → ERROR: {e!r}")

async def main():
    sem = asyncio.Semaphore(CONCURRENT)
    tasks = []
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i in range(1, N_REQUESTS+1):
            async def bound(ii=i):
                async with sem:
                    await send_predict(session, ii)
            tasks.append(asyncio.create_task(bound()))
        await asyncio.wait(tasks, timeout=(MAX_DELAY+TIMEOUT)*2)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print("Done in", round(time.time()-start,2), "s")