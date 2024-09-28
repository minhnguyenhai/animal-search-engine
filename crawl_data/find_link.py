import asyncio
from bs4 import BeautifulSoup
from aiohttp.client_exceptions import ServerDisconnectedError, ClientError

async def find_wiki_en(session, animal_name):
    original_name = animal_name
    animal_name = animal_name[0].upper() + animal_name[1:].lower()
    animal_name = animal_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{animal_name}"
    
    # Try 3 times if the connection is disconnected
    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return True, url
                else:
                    with open("crawl_data/log/log_name_en.txt", "a", encoding="utf-8") as f:
                        f.write(original_name + "\n")
                    return False, None
        except (ServerDisconnectedError, ClientError) as e:
            if attempt == retries - 1:
                print(f"erorr load in {url}, write to log file")
                with open("crawl_data/log/log_internet.txt", "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                return False, None
            
            await asyncio.sleep(2)  # Wait 2 seconds before trying again

async def find_wiki_vn(session, animal_name, wiki_en_url):
    retries = 3 # number of retries
    for attempt in range(retries):
        try:
            async with session.get(wiki_en_url, timeout=30) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    try:
                        # find the link to the Vietnamese wiki page
                        wiki_vn_url = soup.find("a", lang="vi")["href"]
                        return True, wiki_vn_url
                    except:
                        with open("crawl_data/log/log_name_vn.txt", "a", encoding="utf-8") as f:
                            f.write(animal_name + "\n")
                        return False, None
                else:
                    with open("crawl_data/log/log_internet.txt", "a", encoding="utf-8") as f:
                        f.write(wiki_en_url + "\n")
                    return False, None
        
        # Catch internet connection errors and retry
        except (ServerDisconnectedError, ClientError, asyncio.TimeoutError) as e:
            
            if attempt == retries - 1: # If all retries failed, write to log file
                print(f"error load in {wiki_en_url}, write to log file")
                return False, None
            await asyncio.sleep(2)  # wait 2 seconds before trying again

        except Exception as e:  #other errors
            print(f"Unexpected error on attempt {attempt + 1} for {wiki_en_url}: {e}")
            return False, None