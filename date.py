from bs4 import BeautifulSoup
import requests
import datetime


stop_coronavirus = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/'

try:
    html_page = requests.get(stop_coronavirus)
except requests.exceptions.RequestException as e: 
    print (e)
bs = BeautifulSoup(html_page.content, 'html.parser')

search_date = bs.find('div', {'class': 'd-map__title'})
search_date_str = str(search_date)
search_date_str_clear = search_date_str.replace('<div class="d-map__title"><h2>', '')
search_date_str_clear = search_date_str_clear.replace('<span>', ' ')
search_date_str_clear = search_date_str_clear.replace('</span></h2></div>', ':')

dict = {'Name': 'AndreyEx', 'Age': 18}
res = str(dict.get('country'))
print(res)

#res = '\n\n' + search_date_str_clear

#print(res)