
# the main file where every actual this is connected 

import asyncio
import aiohttp
import time

from db import (
    init_db,
    get_active_urls,
    upsert_url_status,
    insert_error_event
)
from status_rules import classify_status


# ---- config ----
CONCURRENCY_LIMIT = 5
MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 10

semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)


# ---- core checker ----
async def check_url(
    session: aiohttp.ClientSession,
    url_id: int,
    url: str
):
    start_time = time.time()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with semaphore:
                async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
                    response_time_ms = round(
                        (time.time() - start_time) * 1000, 2
                    )

                    status_type = classify_status(response.status)

                    print(
                        f"[{url}] -> {response.status} ({status_type})"
                    )

                    # store latest status (summary)
                    upsert_url_status(
                        url_id,
                        response.status,
                        response_time_ms,
                        None
                    )

                    # store error evidence
                    if status_type in ("client_error", "system_error"):
                        insert_error_event(
                            url_id,
                            response.status,
                            status_type
                        )

                    return

        except Exception as e:
            if attempt == MAX_RETRIES:
                response_time_ms = round(
                    (time.time() - start_time) * 1000, 2
                )

                print(f"[{url}] -> ERROR ({e})")

                # summary table
                upsert_url_status(
                    url_id,
                    None,
                    response_time_ms,
                    str(e)
                )

                # error evidence
                insert_error_event(
                    url_id,
                    None,
                    "system_error"
                )
                return

            await asyncio.sleep(RETRY_DELAY)


# ---- runner ----
async def run_checks():
    urls = get_active_urls()

    if not urls:
        print("No active URLs to monitor")
        return

    async with aiohttp.ClientSession() as session:
        tasks = [
            check_url(session, url_id, url)
            for url_id, url, _ in urls
        ]

        await asyncio.gather(*tasks)


# ---- entry point ----
if __name__ == "__main__":
    init_db()
    asyncio.run(run_checks())
    print("Monitoring cycle completed")
