import requests
from bs4 import BeautifulSoup
from ebooklib import epub

# res = requests.get("https://ln.hako.vn/truyen/14960-the-hidden-strongest-knight-executed-in-the-kingdom-as-a-traitor")

# print(res)
# if res.status_code != 200:
#     print("error: response code isn't 200")
# soup = BeautifulSoup(res.content, "html.parser")

# testing
res = open("./sample/sample.html", "r", encoding="utf8").read()
soup = BeautifulSoup(res, "html.parser")

volume_list = soup.find_all("section", "volume-list at-series basic-section volume-mobile gradual-mobile")
author = " ".join(soup.find("span", "info-value").text.split())  # ???
for volume in volume_list:
    volume_id = volume.find("header", "sect-header").get("id").split("_")[1]
    volume_title = volume.find("span", "sect-title").contents[0].strip()
    chapter_list = volume.find("ul", "list-chapters at-series").find_all("li")

    book = epub.EpubBook()
    book.set_identifier(volume_id)
    book.set_title(volume_title)
    book.set_language("vi")
    book.add_author(author)

    book.toc = []
    book.spine = ["nav"]

    css = """
.title {
    font-size: 1.00em;
    text-align: center;
    margin-top: 0.42em;
    margin-bottom: 0.42em;
    margin-left: 0.00em;
    margin-right: 0.00em;
    text-indent: 0.00em;
    line-height: normal;
}

.subtitle {
    font-size: 0.75em;
    text-align: center;
    margin-top: 0.42em;
    margin-bottom: 0.42em;
    margin-left: 0.00em;
    margin-right: 0.00em;
    text-indent: 0.00em;
    line-height: normal;
}

p {
    font-size: 1.00em;
    margin-top: 0.42em;
    margin-bottom: 0.42em;
    margin-left: 0.00em;
    margin-right: 0.00em;
    text-indent: 2.54em;
    line-height: normal;
}

img {
    top: 0px;
    vertical-align: top;
    height: 100%;
}
"""

    book.add_item(epub.EpubItem(uid="style", file_name="static/style.css", media_type="text/css", content=css))

    for chapter in chapter_list:
        chapter_link = "https://ln.hako.vn" + chapter.find("div", "chapter-name").find("a").get("href")
        chapter_id = chapter_link.split("/")[-1].split("-")[0]
        chapter_title = chapter.find("div", "chapter-name").find("a").get("title")

        html_content = open("./sample/chapter.html", "r", encoding="utf8").read()
        chapterSoup = BeautifulSoup(html_content, "html.parser")

        content = ""
        content += '<p class="title">{title}</p>\n'.format(title=volume_title)
        content += '<p class="subtitle">{subtitle}</p>\n'.format(subtitle=chapter_title)

        chapter_content = chapterSoup.find("div", {"id": "chapter-content"}).find_all("p")

        for p in chapter_content:
            if p.find("img"):
                # handle requesting image
                img_link = p.find("img").get("src")
                img_content = open("./sample/sample_img.jpg", "rb").read()

                img_uid = img_link.split("/")[-1].split(".")[0]
                img = epub.EpubImage(
                    uid=img_uid, file_name=img_uid + ".jpg", media_type="image/jpeg", content=img_content
                )
                book.add_item(img)
                content += '<img src="images/{img_uid}.jpg">\n'.format(img_uid=img_uid)
            else:
                content += str(p)

        c = epub.EpubHtml(title=chapter_title, file_name=chapter_id + ".xhtml", lang="vi")
        c.content = content
        book.add_item(c)
        book.toc.append(c)
        book.spine.append(c)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub("test.epub", book, {})
