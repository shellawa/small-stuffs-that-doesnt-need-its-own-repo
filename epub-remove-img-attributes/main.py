from bs4 import BeautifulSoup as bs
import os
import shutil
import zipfile

file_name = "a.epub"

with zipfile.ZipFile(file_name, "r") as zip:
    zip.printdir()
    zip.extractall("./" + file_name.split(".")[0])

folder = "./" + file_name.split(".")[0]
for chapter in os.listdir(folder + "/EPUB/"):
    if not ".xhtml" in chapter:
        continue
    soup = bs(open(folder + "/EPUB/" + chapter, encoding="utf-8"), "html.parser")
    for img in soup.find_all("img"):
        for attr in dict(img.attrs):
            if attr != "src":
                del img.attrs[attr]
    with open(folder + "/EPUB/" + chapter, "w", encoding="utf-8") as file:
        file.write(str(soup))


with zipfile.ZipFile("modified_" + file_name, "w", zipfile.ZIP_DEFLATED) as zip_ref:
    for folder_name, subfolders, filenames in os.walk(folder):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            zip_ref.write(file_path, arcname=os.path.relpath(file_path, folder))

zip_ref.close()

shutil.rmtree(folder)
