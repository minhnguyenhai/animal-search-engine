# đầu vào là tên một con vật bằng tiếng anh, thực hiện search google
import requests
from bs4 import BeautifulSoup 
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import time




async def find_wiki_en(session, animal_name):
    original_name = animal_name
    animal_name = animal_name[0].upper() + animal_name[1:].lower()
    animal_name = animal_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{animal_name}"
    async with session.get(url) as response:
        if response.status == 200:
            return True, url
        else:
            with open("crawl_data/log/log_name_en.txt", "a", encoding="utf-8") as f:
                f.write(original_name + "\n")
            return False, None


async def find_wiki_vn(session, animal_name, wiki_en_url):
    async with session.get(wiki_en_url) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            try:
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
    
    async with session.get(wiki_vn_url) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            # (Tiếp tục như cũ cho phần xử lý nội dung)
            # Lưu JSON...
            #get title in head
            title = soup.find("title").text
            #remove " – Wikipedia tiếng Việt" in title
            title = title[:-23]
            #main content
            all_text = soup.find("div", class_="mw-content-ltr mw-parser-output")
            side_table= all_text.find("table", class_="infobox taxobox")
            if side_table:
                first_img = get_first_img(side_table)

            #get description of animal
            p = all_text.find("p")
            while True:
                try:

                    #nếu the p tìm thấy trống hoặc chỉ chứa dấu cách thì tìm p tiếp theo
                    if p.text.strip() == "" or p.name != "p":
                        p = p.find_next_sibling()
                    else:
                        break
                except:
                    break
            description = p.text
            #thay \n bằng " "
            description = description.replace("\n", " ")

            while True:
                try:
                    p = p.find_next_sibling()
                    if p.name == "p":
                        description += p.text
                    else:
                        break
                except:
                    break
            #get the remaining text as content
            #tìm tất cả các tag cùng cấp với p đằng sau p
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
            #lấy tag phân loài
            classify = get_ani_classify(side_table)
            #save to json file
            data = {
                "title": title,
                "classify": classify,
                "description": description,
                "first_img": first_img,
                "content": content
            }
            with open("crawl_data/content/"+str(couit)+". "+title+".json", "w", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False,indent=4)) #ensure_ascii=False to save unicode character
        else:
            with open("crawl_data/log/log_internet.txt", "a", encoding="utf-8") as f:
                f.write(wiki_vn_url + "\n")


async def process_animal(session, animal, couit):
    check, wiki_en_url = await find_wiki_en(session, animal)
    if check:
        check, wiki_vn_url = await find_wiki_vn(session, animal, wiki_en_url)
        if check:
            await crawl_content_wiki(session, wiki_vn_url, couit)


async def main():

    animalds = ["mammals", "mollusk", "birds", "amphibia", "reptiles"]
    couit = 0
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ani in animalds:
            with open(f"crawl_data/list_name/{ani}.txt", "r", encoding="utf-8") as f:
                animals = [line.strip() for line in f.readlines()]
            inner_count = 0
            for animal in animals:
                if inner_count == 5:
                    await asyncio.gather(*tasks)
                    tasks = []
                    inner_count = 0
                task = process_animal(session, animal, couit)
                tasks.append(task)
                couit += 1
                inner_count += 1
                # print(time.time()-start)

                
        


# Chạy hàm chính
asyncio.run(main())





