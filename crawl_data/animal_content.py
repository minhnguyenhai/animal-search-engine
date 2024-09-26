# đầu vào là tên một con vật bằng tiếng anh, thực hiện search google
import requests
from bs4 import BeautifulSoup 
import json




def find_wiki_en(animal_name):
    #convert to lower case with first letter is upper case
    original_name = animal_name
    animal_name = animal_name.lower()
    animal_name = animal_name[0].upper() + animal_name[1:]
    #repqlce space with _
    animal_name = animal_name.replace(" ", "_")
    #search wiki
    url = "https://en.wikipedia.org/wiki/"+animal_name
    page = requests.get(url)
    if page.status_code == 200:
        return True, url
    else:
        with open("crawl_data/log/log_name_en.txt", "a", encoding="utf-8") as f:
            f.write(original_name + "\n")
        return False, None


def find_wiki_vn(animal_name,wiki_en_url):
    response = requests.get(wiki_en_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
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
    
def crawl_content_wiki(wiki_vn_url, couit):
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

    response = requests.get(wiki_vn_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
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
        return None


#test
#duyệt qua thư mục list_name và lấy tên các file
#mở từng file và đọc từng dòng
animalds = ["mammals","mollusk","birds", "amphibia", "reptiles"]
couit = 0
for ani in animalds:
    with open("crawl_data/list_name/"+ani+".txt", "r", encoding="utf-8") as f:
        animals = f.readlines()
    for animal in animals:
        animal = animal.strip()
        print(animal)
        check, wiki_en_url = find_wiki_en(animal)
        if check:
            check, wiki_vn_url = find_wiki_vn(animal, wiki_en_url)
            if check:
                crawl_content_wiki(wiki_vn_url,couit)
                couit += 1
            else:
                print("Can't find wiki vi")
        else:
            print("Can't find wiki en")







