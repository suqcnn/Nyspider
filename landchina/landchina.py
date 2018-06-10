# -*- coding: utf-8 -*-

from util import *
from bs4 import BeautifulSoup
import codecs
import json


def get_item_list(date_limit, province):
    nodes = {
        '广东省': '44'
    }
    select_district = nodes[province]+'▓~'+province
    page = 1
    result = []
    while True:
        data = {
            'hidComName': "default",
            'TAB_QueryConditionItem': ['9f2c3acd-0256-4da2-a659-6949c4671a2a', 'ec9f9d83-914e-4c57-8c8d-2c57185e912a'],
            'TAB_QuerySubmitConditionData': "9f2c3acd-0256-4da2-a659-6949c4671a2a:{}|42ad98ae-c46a-40aa-aacc-c0884036eeaf:{}".format(date_limit, select_district).encode('GBK'),
            'TAB_QuerySubmitOrderData': "",
            'TAB_RowButtonActionControl': "",
            'TAB_QuerySubmitPagerData': page,
            'TAB_QuerySubmitSortData': ""
        }
        req = build_request(
            url='http://www.landchina.com/default.aspx?tabid=263', data=data)
        table = BeautifulSoup(req.text, 'lxml').find(
            'table', id='TAB_contentTable').find_all('tr')
        if '没有检索到相关数据' in str(table):
            break
        for item in table:
            try:
                line = ['http://www.landchina.com/'+item.find('a').get('href')]
            except:
                continue
            for td in item.find_all('td'):
                try:
                    line.append(td.get_text().replace(
                        '\r', '').replace('\n', ''))
                except:
                    line.append('')
            result.append(line)
        print(date_limit, 'Page', page, 'OK')
        if len(table) < 31:
            break
        page += 1
    return result


def get_item_info(url):
    req = build_request(url)
    table = BeautifulSoup(req.text, 'lxml').find(
        'table', id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1')
    tr_ids = ['mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r17', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r16', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20',
              'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r12', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r9', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r23', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r21', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r10', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14']
    line = ''
    for trid in tr_ids:
        if trid == 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r12':
            try:
                trs = table.find('tr', id=trid).find(
                    'table', id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3').find_all('tr')
                text = '|分期支付约定:'
                for tr in trs:
                    if 'r2_tmp' in str(tr) or 'p1_f3_r1' in str(tr):
                        continue
                    for td in tr.find_all('td'):
                        text += td.get_text()+' '
            except:
                continue
        elif trid == 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r21':
            try:
                tr = table.find('tr', id=trid)
            except:
                continue
            try:
                down = tr.find(
                    'td', id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c2').get_text()
            except:
                down = ''
            try:
                up = tr.find(
                    'td', id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c4').get_text()
            except:
                up = ''
            try:
                date = tr.find(
                    'td', id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r21_c4').get_text()
            except:
                date = ''
            text = '|约定容积率下限:'+down+'|约定容积率上限:'+up+'|约定交地时间:'+date
        else:
            try:
                tds = table.find('tr', id=trid).find_all('td')
            except:
                continue
            text = ''
            for td in tds:
                text += '| '+td.get_text()
        line += text
    line = line.replace('\r', '').replace('\n', '').replace('\t', '').replace(
        '||', '|').replace('||', '|').replace('：', ':').replace(':|', ':')
    item = {}
    keys = []
    for key_value in line.split('|'):
        key = key_value.split(':')[0]
        if key.replace(' ', '').replace('\xa0', '') == '':
            continue
        keys.append(key)
        try:
            item[key] = key_value.split(':')[1]
        except:
            item[key] = ''
    if item[' 面积(公顷)'] == item[' 土地来源']:
        item[' 土地来源'] = '现有建设用地'
    elif float(item[' 土地来源']) == 0:
        item[' 土地来源'] = '新增建设用地'
    else:
        item[' 土地来源'] = '新增建设用地(来自存量库)'
    item['url'] = url
    return item


def get_province_items():
    province = '广东省'
    date_from = '2018-02-20'
    date_to = '2018-02-23'
    current_date = date_from
    while current_date != date_to:
        date = '-'.join([str(int(value)) for value in current_date.split('-')])
        try:
            result = get_item_list(date+'~'+date, province)
        except Exception as e:
            failed = codecs.open('./files/date_failed.txt',
                                 'a', encoding='utf-8')
            failed.write(current_date+'\n')
            failed.close()
            current_date = get_next_date(current_date)
            continue
        f = codecs.open('./files/items.txt', 'a', encoding='utf-8')
        for item in result:
            f.write(json.dumps(item, ensure_ascii=False)+'\n')
        f.close()
        current_date = get_next_date(current_date)
        print(current_time(), 'Date:', current_date, 'OK')


def crawl_info():
    for line in codecs.open('./files/items.txt', 'r', encoding='utf-8'):
        item = json.loads(line)
        try:
            info_item = get_item_info(item[0])
        except Exception as e:
            failed = codecs.open('./files/info_failed.txt',
                                 'a', encoding='utf-8')
            failed.write(line)
            failed.close()
            print(item[0], 'fail')
            continue
        with codecs.open('./files/result.txt', 'a', encoding='utf-8') as f:
            f.write(json.dumps(info_item, ensure_ascii=False)+'\n')
        print(current_time(), item[0], 'OK')


def load_result():
    keys = [' 行政区', ' 电子监管号', ' 项目名称', ' 项目位置', ' 面积(公顷)', ' 土地来源', ' 土地用途', ' 供地方式', ' 土地使用年限', ' 行业分类', ' 土地级别', ' 成交价格(万元)',
            '分期支付约定', ' 土地使用权人', '约定容积率下限', '约定容积率上限', '约定交地时间', ' 约定开工时间', ' 约定竣工时间', ' 实际开工时间', ' 实际竣工时间', ' 批准单位', ' 合同签订日期', 'url']
    yield keys
    for line in codecs.open('./files/result.txt', 'r', encoding='utf-8'):
        item = json.loads(line)
        line = []
        for key in keys:
            try:
                value = item[key]
                if '约定容积率' in key:
                    try:
                        num = float(value)
                    except:
                        value = ''
            except:
                value = ''
            line.append(value)
        yield line


get_province_items()
crawl_info()
write_to_excel(load_result(),'result.xlsx')
