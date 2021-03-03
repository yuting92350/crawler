import pandas as pd
import numpy as np
import requests as rq
import bs4
import re

def Get_label(root):
    source = rq.get(root)
    soup = bs4.BeautifulSoup(source.text, "html.parser")
    typed = soup.find_all("td", class_="t10")

    # get label text
    # not_wanted = ['上市', '上櫃', '股號排序', '股價排序', '漲幅排序', '跌幅排序', '成交量排序']
    # name = [i.string for i in typed[0].find_all("option") if i.string not in not_wanted]
    #
    # # get name list
    # page_num = [re.findall('value="(.*)"', str(i))[0] for i in typed[0].find_all("option")]
    # not_wanted = ['EB011000E', 'EB141000B', 'EB098000E', 'I', 'R', 'P', 'Q', 'V']
    # page_num = [i for i in page_num if i not in not_wanted]

    name = [i.string for i in typed[0].find_all("option")]
    name = np.array(name)[2:-5]
    name = np.delete(name,28)

    page_num = [re.findall('value="(.*)"', str(i))[0] for i in typed[0].find_all("option")]
    page_num = np.array(page_num)[2:-5]
    page_num = np.delete(page_num,28)
    # get page_num
    page_num_dict = {}
    for i, j in zip(page_num, name):
        page_num_dict[i] = j
    # build dict for k:page_num/v:name

    return name,page_num,page_num_dict


def Get_dict(page_num, page_dict):
    _dict = {}
    not_found = []

    for pn in page_num:
        table = pd.read_html(f"https://fubon-ebrokerdj.fbs.com.tw/z/ze/zeg/zeg_{pn}_I.djhtm", encoding="big5hkscs")
        df_table=pd.DataFrame(table[2])

        # get whole table
        col = df_table[1:2]
        df_table.columns = col.values[0]
        df_table =df_table.iloc[2:, :]

        # rename col and drop redundant values
        tmp = df_table.股票名稱.values
        num_name = []
        try:
            for i in tmp:
                num_name.append([re.findall('\'([\w~\u4E00-\u9FFFh~+~＆+-~*~\ ]+)\'', i)[0],re.findall('\'([\w~\u4E00-\u9FFFh~+~＆+-~*~\ ]+)\'', i)[1]])
            df_table['股票名稱'] = np.array(num_name)[:, 1]
            df_table['股票代號'] = np.array(num_name)[:, 0]
            df_table = df_table.reset_index(drop=True)
            _dict[page_dict[pn]] = df_table
        except:
            not_found.append(pn)

    return _dict



if '__main__' == __name__:

    name, page_num, page_dict = Get_label("https://fubon-ebrokerdj.fbs.com.tw/z/ze/zeg/zeg_EB011000E_I.djhtm")

    _dict = Get_dict(page_num, page_dict)

    print(_dict['水泥'])

