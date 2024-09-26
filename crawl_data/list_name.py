from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


# crawl list name of animals using selenium
def crawl_list_name(driver):
      print("Start crawling list name...")
      #make a list of animal groups
      animalds = ["mammals","mollusk","birds", "amphibia", "reptiles"]
      number= [6352,4910,10363, 3424, 4468]
      
      #start crawl
      number_each_group = {"mammals":0, "mollusk":0, "birds":0, "amphibia":0, "reptiles:":0}
      for ani in animalds:
            #open link and click load more to load all animals
            driver.get("https://animalia.bio/"+ani)
            time.sleep(5)
            load_more = driver.find_elements(By.XPATH, "//span[@class='load-more']")[0]
            number_of_click = number[animalds.index(ani)]//42 + 1
            for i in range(int(number_of_click)):
                  try:
                        load_more.click()
                        time.sleep(2)
                  except:
                        continue
            time.sleep(5)

            # make a list of animals
            div=driver.find_element(By.XPATH, "//div[@class='block-animals']")
            list_div = div.find_elements(By.XPATH, "./*")
            print("number of div: ", len(list_div))

            animals = []
            for div in list_div:
                  if div.tag_name == "a":
                        animals.append(div)
            number_each_group[ani] = len(animals)
            #get name of animals and write to file
            with open("/crawl_data/list_name/" + ani+".txt", "a", encoding="utf-8") as f:
                  for animal in animals:
                        f.write(animal.text.split("\n")[0] + "\n")

      print("Finish crawling list name!")
      return number_each_group

