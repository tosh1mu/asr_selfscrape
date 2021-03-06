#coding:utf-8

import lxml.html
from selenium import webdriver
import re
import time
from datetime import datetime
import pandas as pd

def get_root(target_url):
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])

    page_get = False
    root = None

    retry_count = 0
    unit_wait_time = 2

    while not(page_get):
        try:
            print('Trying to get html from ' + target_url + '...')
            driver.get(target_url)
            root = lxml.html.fromstring(driver.page_source)
        except:
            print('Failed. Waiting for a while...')
            retry_count = retry_count + 1
            time.sleep(unit_wait_time * retry_count)
        else:
            print('Succeeded.')
            page_get = True

    return root

def get_areas(root):
    area_dict = {}

    for area in root.cssselect('#main > #main-right > #content-area > #office_search_static_url_form_office > table.office_search_box > tbody > tr > td.select > #area > option'):
        area_code = area.get('value')
        area_name = area.text
        if area_code == '':
            area_dict['offices'] = area_name
        else:
            area_dict[area_code] = area_name

    return area_dict

def get_next_path(root):
    next_path = '#'
    try:
        next_path = root.cssselect('#main > #main-right > #content-area > div.pager-area > div.pagination > ul > li.next.next_page > a')[0].get('href')
    except:
        pass
    return next_path

def get_office_divs(root):
    return root.cssselect('#main > #main-right > #content-area > #office-list-area > div.office-list.gradient-gray.jico')

def chk_type(office_div):
    office_type = 'Free'
    if len(office_div.cssselect('div.cv_box')) > 0:
        office_type = 'Paid'

    return office_type

def get_area(office_div):
    area = None
    return area

def get_office_name(office_div):
    office_name = None
    try:
        office_name = office_div.cssselect('div.detail_box > div.office_name > h3 > a')[0].text
    except:
        print('***WARNING***: Could not get the office name.')
        pass
    return office_name

def get_office_address(office_div):
    office_address = None
    try:
        for td in office_div.cssselect('div.detaili_box > div.office_data > div.data_box > table > tbody > tr > td'):
            print(td.text)
    except:
        pass
    return office_address

def get_office_info(office_div):
    info_dict = {}
    info_dict['type'] = chk_type(office_div)
    info_dict['area'] = get_office_area
    info_dict['office_name'] = get_office_name
    info_dict['address'] = get_office_address
    return info_dict

def reg_office_info(df, office_info):
    info_data = pd.Series(['jico', office_info['area'], office_info['office_name'], office_info['address']],index=['Jiken', 'Area', 'Type', 'Office', 'Address'])
    df = df.append(info_data, ignore_index=True)
    return True

root_url = 'https://jico-pro.com'

start_path = '/offices/'
start_url = root_url + start_path
start_root = get_root(start_url)

area_dict = get_areas(start_root)
dataframe = pd.DataFrame(columns=['Jiken','Area','Type','Office','Address'])

for office_div in get_office_divs(start_root):
    print(get_office_address(office_div))

# for area_code in area_dict.keys():
#     target_urls = []
#     first_url = root_url + '/' + area_code + '/'
#     target_urls.append(first_url)
#
#     while(len(target_urls) > 0):
#         target_url = target_urls.pop(0)
#         root = get_root(target_url)
#
#         for office_div in get_office_divs(root):
#             office_info = get_office_info(office_div)
#             reg_office_info(dataframe, office_info)
#
#         next_path = get_next_path(root)
#         if next_path != '#':
#             next_url = root_url + next_path
#             target_urls.append(next_url)
#
# dataframe = dataframe.drop_duplicates(['Area','Type','Office','Address'])
# dataframe.to_csv('ricon_offices.csv')
