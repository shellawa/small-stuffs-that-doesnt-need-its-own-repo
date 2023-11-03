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


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, "..")))


with zipfile.ZipFile("modified_" + file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipdir(folder, zipf)

shutil.rmtree(folder)
