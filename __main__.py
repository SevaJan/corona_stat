import datetime
import requests
from bs4 import BeautifulSoup

def get_statistics(parameters):
    country = parameters.get('country')
    region = parameters.get('region')

    if str(country) != 'None':
        return worldometers_info(country)
    elif region == 'Russia':
        return worldometers_info(region)
    else:
        return stopcoronavirus_rf(region)

def worldometers_info(location):
    worldmetersLink = 'https://www.worldometers.info/coronavirus/'

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
    new_y = data_y[1]
    death_y = data_y[3]

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
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days = 1)
    notation = 'Информация за день сбрасывается и обновляется после полуночи по Гринвичу (UTC ±0:00)'
    res = '\n\nСтатистика за {}:\n• Всего заболевших — {},\n• Новые случаи — {},\n• Всего умерших — {},\n• Новые смерти — {},\n• Вылечились — {},\n• Болеют на данный момент — {},\n• В критическом состоянии — {}.\n\nСтатистика за {}:\n• Новые случаи — {},\n• Новые смерти — {}.\n\n{}.'.format(today, *data, yesterday, new_y, death_y, notation)
    
    return ({'result' : str(res)})

def stopcoronavirus_rf(location):
    stop_coronavirus = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/'

    try:
        html_page = requests.get(stop_coronavirus)
    except requests.exceptions.RequestException as e: 
        print (e)
    
    bs = BeautifulSoup(html_page.content, 'html.parser')
    search_regions = bs.find_all('tr')
    search_regions_str = str(search_regions)

    start_global = search_regions_str.find(location)
    start_sick = search_regions_str.find('<span class="d-map__indicator d-map__indicator_sick"></span>', start_global) + len('<span class="d-map__indicator d-map__indicator_sick"></span>')
    start_healed = search_regions_str.find('<span class="d-map__indicator d-map__indicator_healed"></span>', start_global) + len('<span class="d-map__indicator d-map__indicator_healed"></span>')
    start_die = search_regions_str.find('<span class="d-map__indicator d-map__indicator_die"></span>', start_global) + len('<span class="d-map__indicator d-map__indicator_die"></span>')
    
    sick = healed = die = ''

    while search_regions_str[start_sick] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        sick += search_regions_str[start_sick]
        start_sick += 1

    while search_regions_str[start_healed] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        healed += search_regions_str[start_healed]
        start_healed += 1

    while search_regions_str[start_die] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        die += search_regions_str[start_die]
        start_die += 1

    search_date = bs.find('div', {'class': 'd-map__title'})
    search_date_str = str(search_date)
    search_date_str_clear = search_date_str.replace('<div class="d-map__title"><h2>', '')
    search_date_str_clear = search_date_str_clear.replace('<span>', ' ')
    search_date_str_clear = search_date_str_clear.replace('</span></h2></div>', ':')
    res = '\n\n' + search_date_str_clear + '\n' + '• Случаев заболевания — ' + sick + ',\n' + '• Человек выздоровело — ' + healed + ',\n' + '• Человек умерло — ' + die + '.'

    return ({'result' : res})
