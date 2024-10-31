import os

def check_dup():
    path = "crawl_data/crawl/content"
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".json")]
    
    name_set = set()
    for file in files:
        name = file.split(".")[1]
        if name in name_set:
            print(f"Duplicate found: {file}")
            #loại bỏ file trùng
            os.remove(os.path.join(path, file))
        else:
            name_set.add(name)
    print("Done checking duplicates")
    print(f"Total duplicates: {len(files) - len(name_set)}")

if __name__ == "__main__":
    check_dup()
