import requests
from bs4 import BeautifulSoup
import re


def store_page(url, title, content):
    pass


def index_URLs(urls, output_file):
    global new_index
    with open(output_file, "a") as file:
        for url in urls:
            indexed_url = f"{new_index}. {url}"
            try:
                file.write("\n" + indexed_url)
            except:
                pass
            new_index += 1


def request_page(url):
    session = requests.Session()
    try:
        response = session.get(url, allow_redirects=True)
        return response.text
    except requests.exceptions.RequestException as e:
        print("Request failed for: " + url)
        return None


def get_URLs(content):
    pattern = r'"(https?://[^"]+)"'

    links = re.findall(pattern, content)
    return links


def crawl(file, k):
    limit = 10  # This limit is for testing only

    x = 0
    crawl_frontier = open(file)
    for line in crawl_frontier:
        k += 1
        if k >= limit:
            return

        url_strip = line[3:]

        if url_strip != "" and url_strip != " ":
            print("Scraping webpage: " + url_strip)
            page_content = request_page(url_strip)

            if page_content is None:
                continue

            URLs = get_URLs(page_content)

            index_URLs(URLs, file)
            x += 1

        else:
            continue

    crawl_frontier.close()


if __name__ == "__main__":
    new_index = 2
    iteration = 0
    k = 0

    # Specify output destination
    file = "crawl_frontier.txt"
    crawl(file, k)
