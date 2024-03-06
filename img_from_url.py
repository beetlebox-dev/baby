import requests
from bs4 import BeautifulSoup


URL = "https://beetlebox.dev"


from urllib.parse import urlparse
hostname = urlparse("https://a.b.beetlebox.co.uk/a/b?u=v&w=x#id").hostname
print(hostname)



# # user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
# # accept_language = "en-US,en;q=0.9"
# # headers = {"user-agent": user_agent, "accept-language": accept_language}
# # response = requests.get(URL, headers=headers)
#
# response = requests.get(URL)
#
# response.raise_for_status()
#
# raw_html = response.text
#
# # print(raw_html)
#
# # only_img_elems = SoupStrainer("img")
# # # Only parse img tags from document
#
# soup = BeautifulSoup(raw_html, 'lxml')
#
# first_img_elem = soup.find('img')
# # all_img_elems = soup.css.select('img')
#
#
# print(first_img_elem)
# print(first_img_elem['src'])

