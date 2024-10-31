import requests
from bs4 import BeautifulSoup
import time

#dọc file txt từng dòng
with open("crawl_data/crawl/list_name/mammals-_1_.txt", "r", encoding="utf-8") as f:
    for line in f:
        animal_name = line.strip()
        if animal_name == "":
            continue
        original_name = animal_name
        animal_name = animal_name.replace(" ", "+")
        url = f"https://www.google.com/search?q={animal_name}+động+vật"
        #find vietnamese wiki link
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            #find vietnamese wikipedia link in google search, is a link have href = /url?q=https://vi.wikipedia.org/wiki/
            try:
                wiki_vn_url = soup.find("a", href=lambda href: href and "vi.wikipedia.org/wiki/" in href)["href"]
                try:
                    title = soup.find("a", href=lambda href: href and "vi.wikipedia.org/wiki/" in href).find("h3").text
                    #remove the prefix "- Wikipedia tiếng Việt" 
                    title = title.strip()[:-23]
                except:
                    title = ""
                if "upload" in wiki_vn_url:
                    print("just image in", original_name)
                    wiki_vn_link = None
                else:
                    wiki_vn_link = wiki_vn_url[7:wiki_vn_url.find("&")]
                    wiki_vn_link = "https://vi.wikipedia.org/" + wiki_vn_link
            except:
                wiki_vn_link = None
            if wiki_vn_link:
                animal_name = original_name + "  Found" + "  " + title
            else:
                animal_name = original_name + "  Not found"
        else:
            print(response.status_code)
            if response.status_code == 429:
                #sleep 10 seconds
                time.sleep(10) 
            animal_name = original_name + "  error 200"
        print(animal_name)