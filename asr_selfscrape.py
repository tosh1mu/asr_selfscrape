# -*- coding: utf-8 -*-

import sys
import time
import lxml.html
from selenium import webdriver
import pandas as pd

args = sys.argv

jiken_list = ['ricon','souzoku','jiko','roudou','keiji','saiken','saimuseiri']
column_index = ['Jiken','Type','Area','Office','Address']

def chk_jiken():
    jiken = None
    try:
        jiken = args[1]
        if jiken not in jiken_list:
            sys.exit('***ERROR***: Wrong jiken name.')
    except:
        sys.exit('***ERROR***: Invalid input. Please type like \'python asc_selfscrape.py ricon\'.')
    return jiken

def get_root_url(jiken):
    root_url = 'http://'+jiken
    if jiken != 'souzoku':
        root_url = root_url + '-pro.com'
    else:
        root_url = root_url + '-pro.info'
    return root_url

def get_initial_url(jiken):
    initial_url = root_url + '/offices/'
    return initial_url

def get_area_url(area_code):
    area_url = root_url + '/' + area_code + '/'
    return  area_url

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

    for area in root.cssselect('#main > #main-right > #content-area > #office_search_static_url_form_office > #selected-condition > tbody > tr > td > #area > option'):
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
    return root.cssselect('#main > #main-right > #content-area > #office-list-area > div.office-list.gradient-gray')

def chk_type(office_div):
    office_type = 'Other'
    if len(office_div.cssselect('div.office-datahead')) > 0:
        office_type = 'Paid'
    elif len(office_div.cssselect('div.free-office-datahead')) > 0:
        office_type = 'Free'

    return office_type

def get_office_datahead(office_div):
    office_type = chk_type(office_div)
    datahead = None
    if office_type == 'Paid':
        datahead = office_div.cssselect('div.office-datahead')[0]
    elif office_type == 'Free':
        datahead = office_div.cssselect('div.free-office-datahead')[0]
    return datahead

def get_office_area(office_div):
    office_area = None
    datahead = get_office_datahead(office_div)
    try:
        office_area = datahead.cssselect('a > div.office-icon > span.icon-large.address')[0].text
    except:
        pass
    return office_area

def get_office_name(office_div):
    office_name = None
    datahead = get_office_datahead(office_div)
    try:
        office_name = datahead.cssselect('h3.offce-name > a')[1].text
    except:
        pass
    return office_name

def get_office_address(office_div):
    office_address = None
    datahead = get_office_datahead(office_div)
    try:
        office_address = office_div.cssselect('div.office-data > table > tbody > tr > td')[0].text
    except:
        pass
    return office_address

########################
### Common functions ###
########################

def get_office_info(office_div):
    info_dict = {}
    info_dict['type'] = chk_type(office_div)
    info_dict['area'] = get_office_area(office_div)
    info_dict['name'] = get_office_name(office_div)
    info_dict['address'] = get_office_address(office_div)
    return info_dict

def append_office_info(df, office_info):
    info_data = pd.Series([jiken,
                           office_info['type'],
                           office_info['area'],
                           office_info['office_name'],
                           office_info['address']],
                          index = column_index)
    new_df = df.append(info_data, ignore_index=True)
    new_df = new_df.drop_duplicates(['Area','Type','Office','Address'])
    return new_df

def save_dataframe(dataframe):
    csv_name = jiken + '_office_info.csv'
    dataframe.to_csv(csv_name)
    return True

#####################
### Main function ###
#####################

def main():
    initial_url = get_initial_url()
    area_dict = get_areas(get_root(initial_url))
    dataframe = pd.DataFrame(columns=column_index)

    for area_code in area_dict.keys():
        target_urls = []
        first_url = get_area_url(area_code)
        target_urls.append(first_url)

        while( len(target_urls) > 0 ):
            target_url = target_urls.pop(0)
            root = get_root(target_url)

            for office_div in get_office_divs(root):
                office_info = get_office_info(office_div)
                dataframe = append_office_info(dataframe, office_info)

                next_path = get_next_path(root)
                if next_path != '#':
                    next_url = root_url + next_path
                    target_urls.append(next_url)

    save_dataframe(dataframe)
    return 0

#################################################################################

if __name__ == '__main__':
    sys.exit(main())
