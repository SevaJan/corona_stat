import datetime
import requests
from bs4 import BeautifulSoup
import pycbrf
import datetime
import json
# new libraries
import pandas as pd
from pandas.io.json import json_normalize
from googletrans import Translator
from typing import Tuple, List


def get_statistics(parameters):
    world = str(parameters.get('world'))
    russia = str(parameters.get('russia'))
    type_of_currency = str(parameters.get('testinput'))

    #world = 'Vatican City'
    #russia = 'None'
    #type_of_currency = 'None'

    if type_of_currency != 'None':
        return get_rate(type_of_currency)
    elif world == 'World':
        return  message_world_top()
    elif world != 'None':
        stats_of_country(world)
        # return worldometers_info(world) 
    elif russia == 'Russia':
        stats_of_country(russia)
        # return worldometers_info(russia)
    else:
        return stopcoronavirus_rf(russia)

# message_world_top()
# stats_of_country()

# getting statistics of countries from api
def total_stats() -> Tuple:
    json_response_v1 = requests.get('https://coronavirus-tracker-api.herokuapp.com/all').json()

    last_date = list(json_response_v1['confirmed']['locations'][0]['history'].keys())[-1]

    confirmed = json_normalize(json_response_v1['confirmed']['locations'])
    confirmed = confirmed.iloc[:, [0, 1, 3, -2]]
    confirmed.insert(4, "Confirmed for day", confirmed.iloc[:, 2] - confirmed.iloc[:, 3])
    confirmed_total = confirmed['latest'].sum()
    confirmed_difference = confirmed_total - confirmed.iloc[:, -2].sum()
    confirmed.rename(columns={confirmed.columns[2]: 'Latest Confirmed', confirmed.columns[3]: 'Confirmed day before'},
                     inplace=True)
    confirmed = confirmed.groupby(['country', 'country_code'], as_index=False).sum()

    recovered = json_normalize(json_response_v1['recovered']['locations'])
    recovered = recovered.iloc[:, [0, 3, -2]]
    recovered.insert(3, "Recovered for day", recovered.iloc[:, 1] - recovered.iloc[:, 2])
    recovered_total = recovered['latest'].sum()
    recovered_difference = recovered_total - recovered.iloc[:, -2].sum()
    recovered.rename(columns={recovered.columns[1]: 'Latest Recovered', recovered.columns[2]: 'Recovered day before'},
                     inplace=True)
    recovered = recovered.groupby(['country'], as_index=False).sum()

    deaths = json_normalize(json_response_v1['deaths']['locations'])
    deaths = deaths.iloc[:, [0, 3, -2]]
    deaths.insert(3, "Deaths for day", deaths.iloc[:, 1] - deaths.iloc[:, 2])
    deaths_total = deaths['latest'].sum()
    deaths_difference = deaths_total - deaths.iloc[:, -2].sum()
    deaths.rename(columns={deaths.columns[1]: 'Latest Deaths', deaths.columns[2]: 'Deaths day before'}, inplace=True)
    deaths = deaths.groupby(['country'], as_index=False).sum()

    confirmed_recovered = pd.merge(confirmed, recovered, on='country', how='inner')
    merged_stats = pd.merge(confirmed_recovered, deaths, on='country', how='inner')
    merged_stats = merged_stats.sort_values(by='Latest Confirmed', ascending=False)
    merged_stats.reset_index(drop=True, inplace=True)

    merged_stats['country'].replace(to_replace=r'US', value='USA', regex=True, inplace=True)

    return (
        merged_stats, last_date, confirmed_total, confirmed_difference, recovered_total, recovered_difference,
        deaths_total,
        deaths_difference)


# function for emoji flags
OFFSET = 127462 - ord('A')


def flag(code: str) -> str:
    code = code.upper()
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)


# Printing stats message of global and top 3 covid cases
microbe = u'\U0001F9A0'
translator = Translator()


def message_world_top() -> str:
    merged_stats, last_date, confirmed_total, confirmed_difference, recovered_total, recovered_difference, deaths_total, deaths_difference = total_stats()
    covid_stats = [['За все время / за сутки\n'],
                   [microbe, '  <b>Мир</b>\n'],
                   ["Заболели: {:,}".format(confirmed_total), " / {:,}\n".format(confirmed_difference)],
                   ["Вылечились: {:,}".format(recovered_total), " / {:,}\n".format(recovered_difference)],
                   ["Умерли: {:,}".format(deaths_total), " / {:,}\n\n".format(deaths_difference)]]

    for i in range(3):
        covid_stats.append([flag(merged_stats.iloc[i, 1]), '  <b>{}</b>\n'.format(
            translator.translate(merged_stats.iloc[i, 0], src='en', dest='ru').text)])
        covid_stats.append(
            ["Заболели: {:,}".format(merged_stats.iloc[i, 2]), " / {:,}\n".format(merged_stats.iloc[i, 4])])
        covid_stats.append(
            ["Вылечились: {:,}".format(merged_stats.iloc[i, 5]), " / {:,}\n".format(merged_stats.iloc[i, 7])])
        covid_stats.append(
            ["Умерли: {:,}".format(merged_stats.iloc[i, 8]), " / {:,}\n\n".format(merged_stats.iloc[i, 10])])

    string = last_date + '\nПоследние данные по коронавирусу во всем мире, топ-3 стран:\n\n'
    for i in range(len(covid_stats)):
        for j in range(len(covid_stats[i])):
            string += covid_stats[i][j]
        # string +=  '\n'
    return  ({'result' : string})


# Printing stats message of specific country
def stats_of_country(country_name: str) -> str:
    merged_stats, last_date, confirmed_total, confirmed_difference, recovered_total, recovered_difference, deaths_total, deaths_difference = total_stats()
    country_stats = []
    index = merged_stats[merged_stats.country == country_name].index[0]

    country_stats.append(['За все время / за сутки\n'])
    country_stats.append([flag(merged_stats.iloc[index, 1]), '  <b>{}</b>\n'.format(
        translator.translate(merged_stats.iloc[index, 0], src='en', dest='ru').text)])
    country_stats.append(
        ["Заболели: {:,}".format(merged_stats.iloc[index, 2]), " / {:,}\n".format(merged_stats.iloc[index, 4])])
    country_stats.append(
        ["Вылечились: {:,}".format(merged_stats.iloc[index, 5]), " / {:,}\n".format(merged_stats.iloc[index, 7])])
    country_stats.append(
        ["Умерли: {:,}".format(merged_stats.iloc[index, 8]), " / {:,}\n\n".format(merged_stats.iloc[index, 10])])

    country_string = last_date + '\nПоследние данные по коронавирусу:\n\n'
    for i in range(len(country_stats)):
        for j in range(len(country_stats[i])):
            country_string += country_stats[i][j]

    return ({'result' : country_string})


# change path to the json file
path='/Users/vsevolodpodshibyakin/Documents/WA/coronavirus/russia/vadim/synonyms_of_regions.json'
array = json.load(open(path))
dictionary = pd.DataFrame (columns = ['Code','Region'])
for i in range(len(array['values'])):
    dictionary = dictionary.append({'Code' : array['values'][i]['value'] , 'Region' : array['values'][i]['synonyms'][-1]} , ignore_index=True)
# function that connect region code with the name of region
def substitute_codes (code):
    region = dictionary[dictionary['Code'] == code].iloc[0,1]
    return region


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
    start_healed = search_regions.find('"healed":', start_global) + len('"healed":')
    start_died = search_regions.find('"died":', start_global) + len('"died":')
    start_sick_incr = search_regions.find('"sick_incr":', start_global) + len('"sick_incr":')
    start_healed_incr = search_regions.find('"healed_incr":', start_global) + len('"healed_incr":')
    start_died_incr = search_regions.find('"died_incr":', start_global) + len('"died_incr":')

    sick = healed = died = sick_incr = healed_incr = died_incr = ''

    while search_regions[start_sick] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        sick += search_regions[start_sick]
        start_sick += 1

    while search_regions[start_healed] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        healed += search_regions[start_healed]
        start_healed += 1

    while search_regions[start_died] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        died += search_regions[start_died]
        start_died += 1

    while search_regions[start_sick_incr] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        sick_incr += search_regions[start_sick_incr]
        start_sick_incr += 1

    while search_regions[start_healed_incr] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        healed_incr += search_regions[start_healed_incr]
        start_healed_incr += 1

    while search_regions[start_died_incr] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        died_incr += search_regions[start_died_incr]
        start_died_incr += 1

    sick, healed, died, sick_incr, healed_incr, died_incr = "{:,}".format(int(sick)), "{:,}".format(int(healed)), "{:,}".format(int(died)), "{:,}".format(int(sick_incr)), "{:,}".format(int(healed_incr)), "{:,}".format(int(died_incr))

    search_date = str(bs.find_all('small'))
    search_date = search_date.replace('[<small>По состоянию на ', '')
    search_date = search_date.replace('</small>]', '')

    res = search_date + '\nПоследние данные по коронавирусу:\n\nЗа всё время / за сутки\n<b>' + substitute_codes(location) + '</b>\nЗаболели: ' + sick + ' / ' + sick_incr + '\nВылечились: ' + healed + ' / ' + healed_incr + '\nУмерли: ' + died + ' / ' + died_incr

    return ({'result' : res})

def get_rate(type_of_currency):
    today_date = datetime.date.today()
    return {'result' : str(pycbrf.ExchangeRates(today_date)[type_of_currency].rate)}


# def worldometers_info(location):
#     worldmetersLink = 'https://www.worldometers.info/coronavirus/'

#     def data_cleanup(array):
#         L = []
#         for i in array:
#             i = i.replace('+', '')
#             i = i.replace('-', '')
#             i = i.replace(',', '')
            
#             if i == '':
#                 i = '0'
                
#             L.append(i.strip())
            
#         return L

#     try:
#         html_page = requests.get(worldmetersLink)
#     except requests.exceptions.RequestException as e: 
#         print (e)
        
#     bs = BeautifulSoup(html_page.content, 'html.parser')
#     search_day = bs.find('div', {'id': 'nav-yesterday'})
#     search = search_day.select('tbody tr td')
#     start = -1
        
#     for i in range(len(search)):
#         if search[i].get_text().find(location) != -1:
#             start = i
#             break
        
#     data = []
        
#     for i in range(1, 8):
#         try:
#             data = data + [search[start + i].get_text()]
#         except:
#             data = data + ['0']

#     data_y = data_cleanup(data)

#     y_recovered = data_y[4]

#     search_day = bs.find('div', {'id': 'nav-today'})
#     search = search_day.select('tbody tr td')
#     start = -1
        
#     for i in range(len(search)):
#         if search[i].get_text().find(location) != -1:
#             start = i
#             break
        
#     data = []
        
#     for i in range(1, 8):
#         try:
#             data = data + [search[start + i].get_text()]
#         except:
#             data = data + ['0']

#     data = data_cleanup(data)

#     t_sick = data[0]
#     t_sick_new = data[1]
#     t_recovered = data[4]
#     if t_recovered == 'N/A':
#         t_recovered = 'Неизвестно'
#     if t_recovered == 'Неизвестно' or y_recovered == 'N/A':
#         t_recovered_new = 'Неизвестно'
#     else:
#         t_recovered_new = int(t_recovered) - int(y_recovered)
#     t_died = data[2]
#     t_died_new = data[3]

#     search_date = str(bs.find_all('div'))
#     start_date = search_date.find('<div style="font-size:13px; color:#999; margin-top:5px; text-align:center">Last updated: ') + len('<div style="font-size:13px; color:#999; margin-top:5px; text-align:center">Last updated: ')
#     date = ''

#     while search_date[start_date] != '<':
#         date += search_date[start_date]
#         start_date += 1

#     if t_sick == '':
#         t_sick = 0
#     if t_sick_new == '':
#         t_sick_new = 0
#     if t_recovered == '':
#         t_recovered = 0
#     if t_recovered_new == '':
#         t_recovered_new = 0
#     if t_died == '':
#         t_died = 0
#     if t_died_new == '':
#         t_died_new = 0
    
#     if t_recovered == 'Неизвестно':
#         t_sick, t_sick_new, t_died, t_died_new = "{:,}".format(int(t_sick)), "{:,}".format(int(t_sick_new)), "{:,}".format(int(t_died)), "{:,}".format(int(t_died_new))
#     elif t_recovered != 'Неизвестно' and t_recovered_new == 'Неизвестно':
#         t_sick, t_sick_new, t_recovered, t_died, t_died_new = "{:,}".format(int(t_sick)), "{:,}".format(int(t_sick_new)), "{:,}".format(int(t_recovered)), "{:,}".format(int(t_died)), "{:,}".format(int(t_died_new))
#     else:   
#         t_sick, t_sick_new, t_recovered, t_recovered_new, t_died, t_died_new = "{:,}".format(int(t_sick)), "{:,}".format(int(t_sick_new)), "{:,}".format(int(t_recovered)), "{:,}".format(int(t_recovered_new)), "{:,}".format(int(t_died)), "{:,}".format(int(t_died_new))

#     res = date + '\nПоследние данные по коронавирусу:\n\nЗа всё время / за сутки\n<b>' + location + '</b>\nЗаболели: ' + t_sick + ' / ' + t_sick_new + '\nВылечились: ' + t_recovered + ' / ' + t_recovered_new + '\nУмерли: ' + t_died + ' / ' + t_died_new

#     return ({'result' : res})