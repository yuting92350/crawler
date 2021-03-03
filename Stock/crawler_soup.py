import pandas as pd
import numpy as np
import requests as rq
import bs4
import re

    # typed_table={ 'EB011000E':'水泥',
    #               'EB012000E':'食品',
    #               'EB013000E':'塑膠',
    #               'EB014000E':'紡織纖維',
    #               'EB015000E':'電機機械',
    #               'EB016000E':'電器電纜',
    #               'EB030000E':'化工',
    #               'EB031000E':'生技醫療',
    #               'EB018000E':'玻璃陶瓷',
    #               'EB019000E':'造紙',
    #               'EB020000E':'鋼鐵',
    #               'EB021000E':'橡膠',
    #               'EB022000E':'汽車',
    #               'EB032000E':'半導體',
    #               'EB033000E':'電腦及週邊設備',
    #               'EB034000E':'光電',
    #               'EB035000E':'通信網路',
    #               'EB036000E':'電子零組件',
    #               'EB037000E':'電子通路',
    #               'EB038000E':'資訊服務',
    #               'EB039000E':'其他電子',
    #               'EB025000E':'建材營造',
    #               'EB026000E':'航運業',
    #               'EB027000E':'觀光',
    #               'EB028000E':'金融保險',
    #               'EB029000E':'貿易公司',
    #               'EB040000E':'油電燃氣',
    #               'EB091000E':'存託憑證',
    #               'EB099000E':'其他',
    #               'EB000000E':'基金',
    #               'EB09990XE':'展延型牛熊證',
    #               'EB09990RE':'特別股公司債'
    #              }


def get_label(root):
    source = rq.get(root)
    soup = bs4.BeautifulSoup(source.text, "html.parser")
    typed = soup.find_all("td", class_="t10")
    # get label text

    # get label text
    name = [i.string for i in typed[0].find_all("option")]
    name = np.array(name)[2:-5]
    name = np.delete(name,28)

    page_num = [re.findall('value="(.*)"', str(i))[0] for i in typed[0].find_all("option")]
    page_num = np.array(page_num)[2:-5]
    page_num = np.delete(page_num,28)

    page_num_dict = {}
    for i, j in zip(page_num, name):
        page_num_dict[i] = j
    # build dict for k:page_num/v:name

    return name, page_num, page_num_dict


def get_code(names):

    codes = []

    for na in names:
        st = str(na.script.contents[0]).index('(')
        ed = str(na.script.contents[0]).index(')')
        tmp = re.findall('\'([\w~\u4E00-\u9FFFh~+~＆+-~*~\ ]+)\'', str(na))

        if len(tmp)==1:
            codes.append(tmp+[''])
        else:
            codes.append(tmp)

    return codes


def get_table(root):

    source = rq.get(root)
    soup = bs4.BeautifulSoup(source.text,"html.parser")
    table = soup.find_all("td",class_=["t3n1","t3g1","t3r1","t3g2","t3r2"])

    #print(table)
    names = soup.find_all("td",class_="t3t1")

    _table = [i.string.strip('%') for i in table]
    _table = np.array(_table).reshape(len(names), -1)

    df_table = pd.DataFrame(_table)

    codes = get_code(names)

    if _table.shape[1] == 7:
        df_table.columns = ["收盤","漲跌","漲跌幅","開盤","最高","最低","成交張數"]
    else:
        df_table.columns = ["收盤","漲跌","漲跌幅","開盤","最高","最低","成交張數","次日漲停","次日跌停"]

    df_table['股票代號'] = np.array(codes).reshape(len(codes), 2)[:, 0]
    df_table['股票名稱'] = np.array(codes).reshape(len(codes), 2)[:, 1]

    df_table = df_table.reset_index(drop=True)

    return df_table


def get_dict(page_num,page_dict):

    _dict = {}
    for pn in page_num:
        df_table = get_table(f"https://fubon-ebrokerdj.fbs.com.tw/z/ze/zeg/zeg_{pn}_I.djhtm")
        _dict[page_dict[pn]] = df_table

    return _dict

if '__main__' == __name__:

    # data, code, ...  = #爬蟲func
    name,page_num,page_dict = get_label("https://fubon-ebrokerdj.fbs.com.tw/z/ze/zeg/zeg_EB011000E_I.djhtm")

    _dict = get_dict(page_num,page_dict)
    print(_dict['水泥'])

