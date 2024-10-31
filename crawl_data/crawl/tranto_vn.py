from deep_translator import GoogleTranslator
import os
path = "crawl_data/crawl/list_name"  # Updated path
vn_path = "crawl_data/crawl/list_name/vn/"  # Updated path
for file in os.listdir(path):
    if file.endswith(".txt"):
        with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
            english_text = f.read()
        
        # Dịch sang tiếng Việt
        translated_text = ""
        for i in range(0, len(english_text), 4999):
            translator = GoogleTranslator(source='en', target='vi')
            part = english_text[i:i+4999]
            translated_text += translator.translate(part)
        print(translated_text)
        
        # Ghi nội dung đã dịch ra file txt mới
        with open(vn_path + file, 'w', encoding='utf-8') as f:
            f.write(translated_text)
            print(f"Đã dịch xong file {file}")

