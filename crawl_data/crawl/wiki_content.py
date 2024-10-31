from bs4 import BeautifulSoup 
import json
import aiohttp
import asyncio
from aiohttp.client_exceptions import ServerDisconnectedError, ClientError
from clean_json import clean
from find_link import find_wiki_en, find_wiki_vn


async def crawl_content_wiki(session, wiki_vn_url, couit):
    def get_first_img(side_table):
        try:
            img = side_table.find("img")["src"]
            #remover"thumb/" in img
            try:
                img = img.replace("thumb/", "")
            except:
                pass
            #just get link from start to first jpg or JPG
            list_ext = [".jpg", ".JPG", ".png", ".PNG", ".jpeg", ".JPEG", ".gif", ".GIF", ".svg", ".SVG", ".webp", ".WEBP"]
            for ext in list_ext:
                if ext in img:
                    img ="https:" + img[:img.index(ext)+len(ext)]
                    break
            return img
        except:
            return ""
        
    def get_ani_classify(side_table):
        list_classify = []
        tbody = side_table.find("tbody")
        if not tbody:
            return list_classify  # Kiểm tra tbody có tồn tại hay không
        
        trs = tbody.find_all("tr")
        found = False
        for tr in trs:
            a = tr.find_all("a")
            
            if not a:
                continue
            text = a[-1].text.strip()  # Xử lý chuỗi gọn hơn
            text1 = a[0].text.strip()
            if text == "Phân loại khoa học" or text1 == "Phân loại khoa học":
                found = True
                continue
        
            if found:
                if tr.find("th",colspan="2"):
                    break
                classify = a[-1].get("title")
                if classify:  # Chỉ thêm nếu có giá trị
                    list_classify.append(classify)
                    
        return list_classify
    # Try 3 times if the connection is disconnected
    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(wiki_vn_url, timeout=10) as response:
                if response.status == 200:
                    try: #try to get all content needed from wiki page
                        soup = BeautifulSoup(await response.text(), 'html.parser')
                        
                        title = soup.find("title").text
                        title = title[:-23]
                        all_text = soup.find("div", class_="mw-content-ltr mw-parser-output")
                        side_table = all_text.find("table", class_="infobox taxobox")

                        #*get first image of animal
                        first_img = get_first_img(side_table) if side_table else ""
                        
                        #*get description of animal and clean it
                        p = all_text.find("p")
                        while True:
                            try:
                                if p.text.strip() == "" or p.name != "p":
                                    p = p.find_next_sibling()
                                else:
                                    break
                            except:
                                break
                        description = p.text
                        description = description.replace("\n", " ")

                        #*get the rest of content
                        while True:
                            try:
                                p = p.find_next_sibling()
                                if p.name == "p":
                                    description += p.text
                                else:
                                    break
                            except:
                                break
                        list_tag= p.find_all_next()
                        content = ""
                        stop_id = ["Chú_thích", "Tham_khảo", "Liên_kết_ngoài", "Xem_thêm"]
                        for tag in list_tag:
                            #nếu gặp thẻ div có thẻ h2 id "Chú_thích", hoặc "Tham_khảo" hoặc "Liên_kết ngoài" hoặc "Xem_thêm" thì dừng
                            if tag.name == "div":
                                if tag.find("h2"): 
                                    if tag.find("h2")["id"] in stop_id:
                                        break
                                    if tag.find("h2")["id"] == "Hình_ảnh":
                                        continue
                                    content += tag.find("h2").text + " "
                                    continue
                            #lấy nội dung của thẻ p
                            if tag.name == "p":
                                content += tag.text + "\n"
                        content = content.replace("\n\n", "\n")


                        #*get classify of animal
                        classify = get_ani_classify(side_table) if side_table else []
                        
                        #*write to json file
                        data = {
                            "title": title,
                            "description": description,
                            "classify": classify,
                            "url": wiki_vn_url,
                            "first_img": first_img,
                            "content": content
                        }
                        with open("crawl_data/crawl/data/content_mini/" + str(couit) + ". " + title + ".json", "w", encoding="utf-8") as f:
                            string_data=json.dumps(data)
                            string_data = clean(string_data)
                            json_data = json.loads(string_data)
                    
                            f.write(json.dumps(json_data, indent=4, ensure_ascii=False))
                            print(f"Crawl {title} successfully")
                        break
                    except:
                        if attempt == retries - 1:
                            with open("crawl_data/crawl/log/log_internet.txt", "a", encoding="utf-8") as f:
                                f.write(wiki_vn_url + "\n")
                                break
                        continue
                else:
                    with open("crawl_data/crawl/log/log_internet.txt", "a", encoding="utf-8") as f:
                        f.write(wiki_vn_url + "\n")
                    break
        except (ServerDisconnectedError, ClientError) as e:
            if attempt == retries - 1:
                with open("crawl_data/crawl/log/log_internet.txt", "a", encoding="utf-8") as f:
                    f.write(wiki_vn_url + "\n")
            print(f"error crawl in {wiki_vn_url}, Try again...")
            await asyncio.sleep(2)


async def process_animal(session, animal, couit):
    check, wiki_en_url = await find_wiki_en(session, animal)
    if check:
        check, wiki_vn_url = await find_wiki_vn(session, animal, wiki_en_url)
        if check:
            await crawl_content_wiki(session, wiki_vn_url, couit)


async def main():
    with open("crawl_data/crawl/log/check_log.txt", "r", encoding="utf-8") as f:
        last_line = f.readlines()[-1].strip()
    
    check = False
    animalds = ["mammals", "mollusk", "birds", "amphibia", "reptiles", "fish", "insects"]
    couit = 0
    
    connector = aiohttp.TCPConnector(limit=50)  # Giới hạn kết nối đồng thời
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for ani in animalds:
            with open(f"crawl_data/list_name/{ani}.txt", "r", encoding="utf-8") as f:
                animals = [line.strip() for line in f.readlines()]
            #each group just crawl 145 animals

            inner_count = 0
            total_in_group = 145
            #Loop 
            for animal in animals:
                if animal == last_line or last_line == "PhamPhong":
                    check = True
                if not check:
                    couit += 1
                    continue
                
                task = process_animal(session, animal, couit)
                tasks.append(task)
                couit += 1
                inner_count += 1
                total_in_group -= 1
                
                if inner_count == 2:
                    await asyncio.gather(*tasks)
                    tasks = []
                    inner_count = 0
                if total_in_group == 0:
                    break
                
                with open("crawl_data/crawl/log/check_log.txt", "w", encoding="utf-8") as f:
                    f.write(animal)


# # Chạy hàm chính
# asyncio.run(main())
