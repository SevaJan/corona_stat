import datetime
import requests
from bs4 import BeautifulSoup
import pycbrf
import datetime
import json
import re

def stopcoronavirus_rf(location):
    location = 'RU-MOW'
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

    print(res)
    return ({'result' : res})

stopcoronavirus_rf('')