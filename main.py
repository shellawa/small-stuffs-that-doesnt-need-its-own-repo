import requests
from bs4 import BeautifulSoup

# res = requests.get("https://ln.hako.vn/truyen/14960-the-hidden-strongest-knight-executed-in-the-kingdom-as-a-traitor")

# print(res)
# if res.status_code != 200:
#     print("error: response code isn't 200")
# soup = BeautifulSoup(res.content, "html.parser")

# testing
res = open("./sample/sample.html", "r", encoding="utf8").read()
soup = BeautifulSoup(res, "html.parser")

f = soup.find_all("section", "volume-list at-series basic-section volume-mobile gradual-mobile")
for volume in f:
    # print(volume.prettify())
    title = volume.find("span", "sect-title")
    print(title.contents[0].strip())
