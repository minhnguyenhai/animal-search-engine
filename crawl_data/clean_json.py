import re


def clean(list_text):
    new_list_text = ''
    # Tạo từ điển để thay thế các ký tự đặc biệt
    dict_replace = {

    }
    dict_replace = {
    '\\u00a0': ' ',   # Non-breaking space
    '\\u02d0': ':',   # Modifier letter triangular colon
    '\\u2013': '-',   # En dash
    '\\u2014': '-',   # Em dash
    '\\u2026': '...',  # Horizontal ellipsis
    '\\u0251': 'ʌ',   # Latin small letter alpha
    '\\u0254': 'ɔ',   # Latin small letter open o
    '\\u0259': 'ə',   # Latin small letter schwa
    '\\u025b': 'ɛ',   # Latin small letter open e
    '\\u025c': 'ɜ',   # Latin small letter reversed open e
    }


    if type(list_text) == str:
        list_text = [list_text]
    for text in list_text:
        text = str(text)
        # Thay thế các ký tự đặc biệt
        for key, value in dict_replace.items():
            text = text.replace(key, value)
        text = text.replace('\\n', '')
        text = text.replace('\\\"', '')
        text = re.sub(r"\[\d\]", '', text)
        text = re.sub(r"\[\d\d\]", '', text)
        text = re.sub(r"\[\d\d\d\]", '', text)

        new_list_text += text
    
    return new_list_text


#duyệt từ json trong folderr content
#clean dữ liệu trong json, lưu lại vào chính file json đó

import os
import json

def clean_json():
    folder = "crawl_data/testdd"
    for file in os.listdir(folder):
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            data = f.read()
            json_data = json.loads(data)
            #chuyển từ json thành chuỗi
            string_data = json.dumps(json_data)
            string_data = clean(string_data)
            json_file = json.loads(string_data)
            # lưu lại vào file json
            with open(os.path.join(folder, file), "w", encoding="utf-8") as f:
                json.dump(json_file, f, ensure_ascii=False, indent=4)
                print(f"Cleaned {file}")


# clean_json()