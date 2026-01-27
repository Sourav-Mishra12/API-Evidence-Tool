import aiohttp
import asyncio
import time 

semaphore = asyncio.Semaphore(5)

MAX_RETRIES = 3
RETRY_DELAY = 1 # isse zyada nahii 


async def url_checker( session : aiohttp.ClientSession ,url : str):  # spying on the URL (sherlock)
    start_time = time.time()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with semaphore:
                async with session.get(url, timeout=10) as response:
                    end_time = time.time()

                    return {
                        "url": url,
                        "status": response.status,
                        "response_time_ms": round((end_time - start_time) * 1000, 2),
                        "error": None
                    }

        except Exception as e:
            if attempt == MAX_RETRIES:
                end_time = time.time()
                return {
                    "url": url,
                    "status": None,
                    "response_time_ms": round((end_time - start_time) * 1000, 2),
                    "error": str(e)
                }

            # wait before retrying
            await asyncio.sleep(RETRY_DELAY)


async def multiple_url_checker(urls: list[str]):
    async with aiohttp.ClientSession() as session:  
      tasks = []

      for url in urls :
          task = asyncio.create_task(url_checker(session , url))
          tasks.append(task)

      result = await asyncio.gather(*tasks)
      return result



async def main():
    urls = [
        "https://example.com",
        "https://google.com",
        "https://httpbin.org/status/500",
        "https://thisurldoesnotexist.xyz"
    ]

    results = await multiple_url_checker(urls)

    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())