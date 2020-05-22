import datetime
import requests
from bs4 import BeautifulSoup
import pycbrf
import datetime
import json
import re

def get_statistics(parameters):
    world = str(parameters.get('world'))
    russia = str(parameters.get('russia'))
    type_of_currency = str(parameters.get('testinput'))

    if type_of_currency != 'None':
        return get_rate(type_of_currency)
    elif world != 'None':
        return worldometers_info(world)
    elif russia == 'Russia':
        return worldometers_info(russia)
    else:
        return stopcoronavirus_rf(russia)

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
    if t_recovered == 'N/A':
        t_recovered = 'Неизвестно'
    if t_recovered == 'Неизвестно' or y_recovered == 'N/A':
        t_recovered_new = 'Неизвестно'
    else:
        t_recovered_new = int(t_recovered) - int(y_recovered)
    t_died = data[2]
    t_died_new = data[3]

    search_date = str(bs.find('div', {'style': 'font-size:13px; color:#999; margin-top:5px; text-align:center'}))
    start_date = search_date.find('Last updated: ') + len('Last updated: ')
    date = ''

    while search_date[start_date] != '<':
        date += search_date[start_date]
        start_date += 1

    if t_sick == '':
        t_sick = 0
    if t_sick_new == '':
        t_sick_new = 0
    if t_recovered == '':
        t_recovered = 0
    if t_recovered_new == '':
        t_recovered_new = 0
    if t_died == '':
        t_died = 0
    if t_died_new == '':
        t_died_new = 0
    
    if t_recovered == 'Неизвестно':
        t_sick, t_sick_new, t_died, t_died_new = "{:,}".format(int(t_sick)), "{:,}".format(int(t_sick_new)), "{:,}".format(int(t_died)), "{:,}".format(int(t_died_new))
    elif t_recovered != 'Неизвестно' and t_recovered_new == 'Неизвестно':
        t_sick, t_sick_new, t_recovered, t_died, t_died_new = "{:,}".format(int(t_sick)), "{:,}".format(int(t_sick_new)), "{:,}".format(int(t_recovered)), "{:,}".format(int(t_died)), "{:,}".format(int(t_died_new))
    else:   
        t_sick, t_sick_new, t_recovered, t_recovered_new, t_died, t_died_new = "{:,}".format(int(t_sick)), "{:,}".format(int(t_sick_new)), "{:,}".format(int(t_recovered)), "{:,}".format(int(t_recovered_new)), "{:,}".format(int(t_died)), "{:,}".format(int(t_died_new))

    res = date + '\nПоследние данные по коронавирусу:\n\nЗа всё время / за сутки\n<b>' + location + '</b>\nЗаболели: ' + t_sick + ' / ' + t_sick_new + '\nВылечились: ' + t_recovered + ' / ' + t_recovered_new + '\nУмерли: ' + t_died + ' / ' + t_died_new

    return ({'result' : res})

def stopcoronavirus_rf(location):
    stop_coronavirus = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/information/'

    try:
        html_page = requests.get(stop_coronavirus)
    except requests.exceptions.RequestException as e: 
        print (e)
        
    bs = BeautifulSoup(html_page.content, 'html.parser')
    search_regions = str(bs.find_all('cv-spread-overview'))
    start_global = search_regions.find(location)

    start_sick = search_regions.find('"sick":', start_global) + len('"sick":')
    start_died_incr = search_regions.find('"died_incr":', start_global) + len('"died_incr":')

    end_of_line = search_regions[start_died_incr:].find('}')
    values = re.findall('(\d+)', search_regions[start_sick:start_died_incr + end_of_line])

    sick, healed, died, sick_incr, healed_incr, died_incr = "{:,}".format(int(values[0])), "{:,}".format(int(values[1])), "{:,}".format(int(values[2])), "{:,}".format(int(values[3])), "{:,}".format(int(values[4])), "{:,}".format(int(values[5]))

    search_date = str(bs.find_all('small'))
    search_date = search_date.replace('[<small>По состоянию на ', '')
    search_date = search_date.replace('</small>]', '')

    res = search_date + '\nПоследние данные по коронавирусу:\n\nЗа всё время / за сутки\n<b>' + location + '</b>\nЗаболели: ' + sick + ' / ' + sick_incr + '\nВылечились: ' + healed + ' / ' + healed_incr + '\nУмерли: ' + died + ' / ' + died_incr

    return ({'result' : res})

def get_rate(type_of_currency):
    today_date = datetime.date.today()
    return {'result' : str(pycbrf.ExchangeRates(today_date)[type_of_currency].rate)}
