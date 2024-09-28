
#có nhiệm vụ tìm kiếm tên loài động vật trên google, trả về link wiki tiếng việt

import asyncio
import aiohttp
from urllib.parse import unquote
from bs4 import BeautifulSoup
from aiohttp.client_exceptions import ServerDisconnectedError, ClientError
from wiki_content import crawl_content_wiki

async def find_google(session, animal_name):
    original_name = animal_name
    animal_name = animal_name.replace(" ", "+")
    url = f"https://www.google.com/search?q={animal_name}+động+vật"
    
    # Try 3 times if the connection is disconnected
    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), 'html.parser')
                    #save the html file
                    # with open("crawl_data/"+original_name+".txt", "w", encoding="utf-8") as f:
                    #     f.write(str(soup))
                    try:
                        # tìm thẻ a có href chứa đoạn vi.wikipedia.org/wiki/
                        wiki_vn_url = soup.find("a", href=lambda href: href and "vi.wikipedia.org/wiki/" in href)["href"]
                        if "upload" in wiki_vn_url:
                            print("just image in", original_name)
                            return False, None
                        wiki_vn_url = unquote(wiki_vn_url)
                        #remove the prefix "/url?q=" and the link after the first "&"
                        wiki_vn_url = wiki_vn_url[7:wiki_vn_url.find("&")]
                        return True, wiki_vn_url
                    except:
                        with open("crawl_data/log/log2.txt", "a", encoding="utf-8") as f:
                            f.write(original_name + "\n")
                        return False, None
                elif response.status == 429:
                    with open("crawl_data/log/log429.txt", "a", encoding="utf-8") as f:
                        f.write(original_name + "\n")
                    return False, None
                else:
                    with open("crawl_data/log/log_internet.txt", "a", encoding="utf-8") as f:
                        f.write(url + "\n")
                    return False, None
        except (ServerDisconnectedError, ClientError) as e:
            if attempt == retries - 1:
                print(f"Error loading {url}, writing to log file")
                with open("crawl_data/log/log_internet.txt", "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                return False, None
            await asyncio.sleep(2)  # Đợi 2 giây trước khi thử lại


# gọi hàm xử lí danh sách tên động vật
async def process_name(session, name_check, count_check):
    check, wiki_vn_url = await find_google(session, name_check)
    if check:
        await crawl_content_wiki(session, wiki_vn_url, count_check)
    else:
        if wiki_vn_url:
            with open("crawl_data/log/log429.txt", "a", encoding="utf-8") as f:
                f.write(wiki_vn_url + "\n")
            
            


async def find_and_crawl():
    animalds = ["mammals", "mollusk", "birds", "amphibia", "reptiles"]
    with open("crawl_data/log/log_name_en.txt", "r", encoding="utf-8") as f:
        en = [line.strip() for line in f.readlines()]
    
    with open("crawl_data/log/log_name_vn.txt", "r", encoding="utf-8") as f:
        vn = [line.strip() for line in f.readlines()]

    with open("crawl_data/log/log429.txt", "r", encoding="utf-8") as f:
        log429 = [line.strip() for line in f.readlines()] if f.readlines() else []

    list_check = en + vn

    total_list = []
    for ani in animalds:
        with open(f"crawl_data/list_name/{ani}.txt", "r", encoding="utf-8") as f:
            animals = [line.strip() for line in f.readlines()]
            print("number of name in ", ani, ":", len(animals))
            total_list += animals
    print("number of name need total: ", len(total_list))
    print("number of name need to check: ", len(list_check))
    couit_check = 0
    connector = aiohttp.TCPConnector(limit=50)  # Giới hạn kết nối đồng thời
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        inner_count = 0
        for i in range(len(list_check)):
            for j in range(len(total_list)):
                if list_check[i] == total_list[j]:
                    inner_count += 1
                    break
                couit_check += 1
            #xoá tên động vật đã duyệt
            task = asyncio.create_task(process_name(session, list_check[i], couit_check))
            couit_check = 0
            tasks.append(task)
            
            if inner_count == 3:
                await asyncio.gather(*tasks)
                tasks = []
                inner_count = 0
        if tasks:
            await asyncio.gather(*tasks)
        with open("crawl_data/log/log429", "r", encoding="utf-8") as f:
            log429 = [line.strip() for line in f.readlines()]
        with open("crawl_data/log/log429.txt", "w", encoding="utf-8") as f:
        #xoá len(log429) dòng đâu tiên trong log429.txt
            for i in range(len(log429)):
                f.write("")
        with open("crawl_data/log/log_name_en.txt", "w", encoding="utf-8") as f:
            for name in log429:
                f.write(name + "\n")
        with open("crawl_data/log/log_name_vn.txt", "a", encoding="utf-8") as f:
            f.write("")
        print("Done")


asyncio.run(find_and_crawl())


        
