from bs4 import BeautifulSoup
import requests


def main():
    lyric_page = "https://genius.com/Lin-manuel-miranda-alexander-hamilton-lyrics"

    response = requests.get(lyric_page)

    soup = BeautifulSoup(response.content, "html.parser")
    a = soup.find("div", attrs={"class": "lyrics"})
    pass

if __name__ == "__main__":
    main()
