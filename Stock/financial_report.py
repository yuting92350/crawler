import numpy as np
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup as bs
import sys
import pickle
import time
from random import randint


def send_request(code,year,season):

    stock_dic = {
        'encodeURIComponent': '1',
        'step': '1',
        'firstin': '1',
        'off': '1',
        'keyword4': '',
        'code1': '',
        'TYPEK2': '',
        'checkbtn': '',
        'queryName': 'co_id',
        'inpuType': 'co_id',
        'TYPEK': 'all',
        'isnew': 'fale',
        'co_id': code,
        'year':year,
        'season':season
    }

    url = "https://mops.twse.com.tw/mops/web/t164sb03"
    headers = {'content-type': 'charset=utf8'}
    res = requests.post(url, data = stock_dic, headers=headers)
    soup = bs(res.text,'lxml')

    return soup


if '__main__' == __name__:

    stock_code_list = ['8112']#, '2330']#, '0050']

    total_df=pd.DataFrame()
    for code in stock_code_list:
        intial = 1
        for year in range(103,109):
            for season in range(1,4):

                soup = send_request(code,year,season)

                dates = [soup.find_all('th',class_='tblHead')[i].getText().lstrip() for i in [3,4,5]]
                new_dates = ['欄位名稱']+ [dates[int(i/2)]+'_1' if i%2==0 else dates[int(i/2)]+'_2' for i in range(6)]


                even=soup.find_all('td',class_=['even', 'odd'])

                content = [i.text.replace(' ', '').replace('\u3000', '') for i in even]
                content = np.array(content).reshape(-1, 7)

                content = content[content[:, 1]!='']
                val = content[:, [0] + [i for i in range(content.shape[1]) if i%2==1]]
                rate = content[:, [i for i in range(content.shape[1]) if i%2==0]]

                val, rate = val.T, rate.T

                val[0] = [i+'_val' for i in val[0]]
                rate[0] = [i+'_rate' for i in rate[0]]

                val_df = pd.DataFrame(val[1:], columns=val[0], index=dates)
                rate_df = pd.DataFrame(rate[1:], columns=rate[0], index=dates)

                df = pd.concat([val_df, rate_df], axis=1)

                exit()

                df = df.iloc[0:-1,0:3]

                if intial == 1:
                    total_df = df
                else:
                    total_df=pd.merge(total_df,df)
                intial = 0
                time.sleep(randint(2, 6))
        total_df = total_df.set_index('欄位名稱')
        print(total_df.columns)
        pickle.dump(total_df, open(f'./chart/{code}.pkl' ,'wb'))






