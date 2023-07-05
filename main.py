import requests
import inquirer
from uuid import uuid4
from bs4 import BeautifulSoup
from ebooklib import epub
from pathlib import Path

novel_link = input("Nhập link của novel (Ctrl + Shift + V để dán link): ")

res = requests.get(novel_link)

if res.status_code != 200:
    print("error: response code isn't 200")
    quit()
soup = BeautifulSoup(res.content, "html.parser")

path = "./output/" + novel_link.split("/")[-1] + "/"

novel_title = soup.find("span", "series-name").text.strip()
if not novel_title:
    print("Novel không hợp lệ!")
    quit()
novel_author = " ".join(soup.find("span", "info-value").text.split())  # ???

volume_list = soup.find_all("section", "volume-list at-series basic-section volume-mobile gradual-mobile")
volume_title_list = [title.find("span", "sect-title").contents[0].strip() for title in volume_list]

selected_title_list = inquirer.prompt(
    [
        inquirer.Checkbox(
            "selected",
            message="Chọn các volume muốn tải (Di chuyển bằng mũi tên, chọn bằng Space, đồng ý bằng Enter)",
            choices=volume_title_list,
            default=volume_title_list,
        )
    ]
)["selected"]
volume_list = [v for v in volume_list if (v.find("span", "sect-title").contents[0].strip() in selected_title_list)]


for volume in volume_list:
    volume_id = volume.find("header", "sect-header").get("id").split("_")[1]
    volume_title = volume.find("span", "sect-title").contents[0].strip()
    cover_link = (
        volume.find("div", "content img-in-ratio")
        .get("style")
        .replace("background-image: url('", "")
        .replace("')", "")
        .replace("-m.jpg", ".jpg")
    )
    cover_content = requests.get(
        cover_link,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.55",
            "Referer": novel_link,
        },
    ).content

    chapter_list = volume.find("ul", "list-chapters at-series").find_all("li")

    book = epub.EpubBook()
    book.set_identifier(volume_id)
    book.set_title(volume_title)
    book.set_language("vi")
    book.add_author(novel_author)
    book.set_cover("cover.jpg", cover_content)

    book.toc = []
    book.spine = ["cover", "nav"]

    css = """
.title {
    font-weight: bold;
    font-size: 1.20em;
    text-align: center;
    margin-top: 0.42em;
    margin-bottom: 0.25em;
    margin-left: 0.00em;
    margin-right: 0.00em;
    text-indent: 0.00em;
    line-height: normal;
}

.subtitle {
    font-weight: bold;
    font-size: 1em;
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
    display:block;
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    margin: 0px auto;
    padding: 15px 10px;
}
"""
    style = epub.EpubItem(uid="style", file_name="static/style.css", media_type="text/css", content=css)
    book.add_item(style)

    for chapter in chapter_list:
        chapter_link = "https://ln.hako.vn" + chapter.find("div", "chapter-name").find("a").get("href")
        chapter_id = chapter_link.split("/")[-1].split("-")[0]
        chapter_title = chapter.find("div", "chapter-name").find("a").get("title")

        html_content = requests.get(chapter_link).content
        chapterSoup = BeautifulSoup(html_content, "html.parser")

        content = ""
        content += '<p class="title">{title}</p>\n'.format(title=volume_title)
        content += '<p class="subtitle">{subtitle}</p>\n'.format(subtitle=chapter_title)

        chapter_content = chapterSoup.find("div", {"id": "chapter-content"}).find_all("p")

        for p in chapter_content:
            if p.find("img"):
                # handle requesting image
                img_link_list = p.find_all("img")
                for img_link in img_link_list:
                    img_content = requests.get(
                        img_link.get("src"),
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.55",
                            "Referer": chapter_link,
                        },
                    ).content

                    img_uid = str(uuid4())
                    img = epub.EpubImage(
                        uid=img_uid,
                        file_name="static/{img_uid}.jpg".format(img_uid=img_uid),
                        media_type="image/jpeg",
                        content=img_content,
                    )
                    book.add_item(img)
                    content += '<img src="static/{img_uid}.jpg">\n'.format(img_uid=img_uid)
            else:
                content += str(p) + "\n"

        c = epub.EpubHtml(title=chapter_title, file_name=chapter_id + ".xhtml", lang="vi")
        c.content = content
        c.add_item(style)
        book.add_item(c)
        book.toc.append(c)
        book.spine.append(c)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    Path(path).mkdir(parents=True, exist_ok=True)
    epub.write_epub(path + volume_title + ".epub", book, {})
