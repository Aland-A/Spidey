import requests
from bs4 import BeautifulSoup
import math
from bitarray import bitarray

index = 1
current_domain = ""  # This is used to append a domain to a path within a domain
checksum = 1
bf_size = 2397000000
bf = bitarray(bf_size)
bf.setall(0)  # initialize all bits to 0
k = 4


def simple_sum_hash(s, m):
    return sum(ord(c) for c in s) % m


def polynomial_hash(s, base=31, prime_mod=1_000_000_009, m=1000):
    hash_val = 0
    for i, c in enumerate(s):
        hash_val = (hash_val + ord(c) * pow(base, i, prime_mod)) % prime_mod
    return hash_val % m


def xor_hash(s, m):
    h = 0
    for c in s:
        h ^= ord(c)
    return h % m


def multiplicative_hash(s, factor=37, m=1000):
    h = 0
    for c in s:
        h = h * factor + ord(c)
    return h % m


def is_member_of_bf(_url_):
    global bf_size
    global bf
    h1 = simple_sum_hash(_url_, bf_size)
    h2 = polynomial_hash(s=_url_, m=bf_size)
    h3 = xor_hash(_url_, bf_size)
    h4 = multiplicative_hash(s=_url_, m=bf_size)
    if bf[h1] and bf[h2] and bf[h3] and bf[h4]:
        return True
    else:
        bf[h1] = bf[h2] = bf[h3] = bf[h4] = 1
        return False


def is_valid(url):
    """
    This function decides whether a given URL is worth exploring, crawling, or indexing.
    For example, any URL that leads to a non-markup (e.g., .pdf, .png, etc) file should return False.
    For now, any URL containing two instances of '.' or two instances of ':' will return False.
    Note that the URL checked here is already a valid web URL.
    The job of this function is to determine whether we are interested in indexing the URL.
    """

    if (
        url.count(":") >= 2
        or (".php" in url)
        or (".png" in url)
        or (".jpg" in url)
        or (".jpeg" in url)
        or (".pdf" in url)
    ):
        return False
    return True


def remove_extra_characters(url):
    return url.replace("%0A", "")


def index_URLs(urls, output_file):
    with open(output_file, "a+") as file:
        for url in urls:
            url = remove_extra_characters(url)
            if is_valid(url) and not is_member_of_bf(url):
                try:
                    file.write("\n" + url)
                except:
                    pass


def store_page(document, url):
    global index
    soup = BeautifulSoup(document, features="lxml")
    text = soup.get_text()
    stripped_text = text.replace("\n\n", "")
    path = "./storage/" + str(index) + ".txt"
    index += 1
    with open(path, "w", encoding="utf-8") as file:
        file.write(url)
        file.write("\n")
        file.write(stripped_text)


def get_URLs(content):
    global current_domain
    soup = BeautifulSoup(content, "html.parser")
    anchor_tags = soup.find_all("a")

    links = []
    for tag in anchor_tags:
        link = tag.get("href")
        if link:
            if link[0] == "/":  # It is a path
                whole_url = current_domain + link
                links.append(whole_url)
            elif (
                link[0] == "h" or link[0] == "H"
            ):  # It start with http, https, HTTP, or HTTPS
                links.append(link)
    return links


def request_page(new_url):
    try:
        response = requests.get(new_url)
        # with open("temp.txt", "w", encoding="utf-8") as file:
        #     file.write(response.text)
        #     file.write("\n")
        #     exit()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Request failed for: " + new_url)
        with open("failed.txt", "w", encoding="utf-8") as file:
            file.write(new_url)
            file.write("\n")
        return None


def crawl(file, k):
    global current_domain
    limit = 27  # This limit is for testing only

    x = 0
    crawl_frontier = open(file)
    for line in crawl_frontier:
        k += 1
        if k >= limit:
            return

        if line != "" and line != " ":
            # If we are crawling a new website, change the current domain
            if line[-4:] in [".com", ".org", "com"]:
                current_domain = line
            print("Scraping webpage: " + line)
            page_content = request_page(line)

            if page_content is None:
                continue

            URLs = get_URLs(page_content)
            store_page(page_content, line)
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
    file = "crawler/frontier.txt"
    crawl(file, k)
