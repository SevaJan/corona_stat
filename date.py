import datetime
import requests
from bs4 import BeautifulSoup

worldmetersLink = 'https://www.worldometers.info/coronavirus/'
location = 'World'

def data_cleanup(array):
    L = []
    for i in array:
        i = i.replace('+', '')
        i = i.replace('-', '')
        i = i.replace(',', '')
        
        if i == '':
            i = '0'
            
        L.append(i.strip())
        
    return L

try:
    html_page = requests.get(worldmetersLink)
except requests.exceptions.RequestException as e: 
    print (e)
    
bs = BeautifulSoup(html_page.content, 'html.parser')
search_day = bs.find('div', {'id': 'nav-yesterday'})
search = search_day.select('tbody tr td')
start = -1
    
for i in range(len(search)):
    if search[i].get_text().find(location) != -1:
        start = i
        break
    
data = []
    
for i in range(1, 8):
    try:
        data = data + [search[start + i].get_text()]
    except:
        data = data + ['0']

data_y = data_cleanup(data)

y_recovered = data_y[4]

search_day = bs.find('div', {'id': 'nav-today'})
search = search_day.select('tbody tr td')
start = -1
    
for i in range(len(search)):
    if search[i].get_text().find(location) != -1:
        start = i
        break
    
data = []
    
for i in range(1, 8):
    try:
        data = data + [search[start + i].get_text()]
    except:
        data = data + ['0']

data = data_cleanup(data)

t_sick = data[0]
t_sick_new = data[1]
t_recovered = data[4]
t_recovered_new = int(t_recovered) - int(y_recovered)
t_died = data[2]
t_died_new = data[3]

search_date = str(bs.find_all('div'))
start_date = search_date.find('<div style="font-size:13px; color:#999; margin-top:5px; text-align:center">Last updated: ') + len('<div style="font-size:13px; color:#999; margin-top:5px; text-align:center">Last updated: ')
date = ''

while search_date[start_date] != '<':
    date += search_date[start_date]
    start_date += 1

t_sick, t_sick_new, t_recovered, t_recovered_new, t_died, t_died_new = "{:,}".format(int(t_sick)), "{:,}".format(int(t_sick_new)), "{:,}".format(int(t_recovered)), "{:,}".format(int(t_recovered_new)), "{:,}".format(int(t_died)), "{:,}".format(int(t_died_new))

res = date + '\nПоследние данные по коронавирусу:\n\nЗа всё время / за сутки\n<b>' + location + '<b>\nЗаболели: ' + t_sick + ' / ' + t_sick_new + '\nВылечились: ' + t_recovered + ' / ' + t_recovered_new + '\nУмерли: ' + t_died + ' / ' + t_died_new

print(res)

#return ({'result' : res})