import os
import time
import random
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

def get_url(code):
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) # url

    return url

def preprocess_df(df):
    # Retype Float -> Int
    df = df.dropna()  # Remove NaN Values
    df = df.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
    df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)

    df = df.drop_duplicates(['date'], keep='last')     # Remove Redundancy Data
    df['date'] = pd.to_datetime(df['date'])    # Retype String to Datetime
    df = df.sort_values(by=['date'], ascending=True)     # Sort in ascending order by Date

    # Sort Index For Row
    df.index = [ i for i in range(len(df.index))]
    df = df.query('2016 <= date.dt.year <= 2020')
    return df

def random_time():
    return random.randrange(2, 3) + random.randrange(1,3) # 크롤링 시간 조정을 위한 random time

def data_save(output_dir, filename, df):
    path = os.path.join(output_dir, filename)
    df.to_csv(path, index=False)

def main():
    if os.path.exists("./naverstock_data"):
        output_dir = "./naverstock_data"
    else:
        os.mkdir("./naverstock_data")
        output_dir = "./naverstock_data"

    df = pd.DataFrame()
    target_bundle_num = 12

    #finanace data에서 수집안된 데이터
    none_code = ['059270', '060080', '142220', '145730', '153760', '158320', '169830', '184390', '199890', '213930', '235370',
                 '236490', '240600', '241660', '244290', '244310', '247580', '252990', '255890', '258840', '259070', '262840',
                 '271530', '272810', '279120', '284710', '285340', '292070', '294080', '298410', '29923L', '30018L', '308460',
                 '309110', '311120', '31134K', '312230', '312800', '313100', '314080', '316320', '321820', '32316K', '336730',
                 '340750', '34385K', '350340', '352700', '352910', '357580', '361670', '367360', '375500', '375770', '376430',
                 '377400', '377630', '38380K', '387270', '390400', '049450', '086710', '113300', '123780', '163290', '169140',
                 '177850', '179090', '187660', '210160', '228980', '234760', '239280', '24251Q', '249680', '250990', '254650',
                 '258340', '258890', '261780', '266930', '276040', '278470', '281630', '283970', '289190', '294570', '298130',
                 '29922L', '300500', '306130', '306920', '31508K', '316840', '318140', '318590', '319810', '322310', '323410',
                 '328130', '332760', '334970', '338220', '34534K', '34695K', '347700', '350990', '352480', '35286N', '355410',
                 '356890', '35732K', '361390', '361610', '363250', '364460', '366330', '367800', '373200', '375270', '375760',
                 '376190', '379660', '379780', '380170', '381570', '383800', '385510', '385590', '385660', '385710', '385720',
                 '004050', '038430', '064470', '067030', '093810', '099430', '106870', '137310', '156000', '177900', '186630',
                 '203900', '226590', '228990', '236810', '239620', '239970', '246780', '248070', '255780', '259210', '259290',
                 '266530', '268200', '276730', '276980', '277290', '277310', '277490', '277810', '280470', '285820', '286340',
                 '289220', '293990', '304720', '30703K', '309740', '311320', '318400', '319700', '322590', '325840', '32904L',
                 '33129K', '333900', '337280', '339610', '340930', '341170', '344540', '347030', '348080', '351330', '357100',
                 '357230', '363260', '368770', '370310', '377030', '378850', '379800', '379810', '380320', '381170', '381180',
                 '385600', '387280', '390350', '390390', '394340', '394660', '394670', '395160', '052920', '064400', '078510',
                 '122230', '134660', '141280', '145940', '163730', '170190', '191390', '194530', '201400', '214240', '226250',
                 '234820', '238820', '240180', '247660', '256970', '262100', '270530', '270730', '271830', '272850', '276960',
                 '27863K', '283770', '285240', '285880', '298210', '299760', '302110', '302440', '303530', '314930', '333450',
                 '333620', '341790', '344250', '348030', '358580', '365270', '366510', '367480', '372290', '373340', '37550K',
                 '376250', '376410', '377990', '379790', '380160', '380340', '380440', '381560', '383220', '383310', '385520',
                 '388280', '388420', '394350']

    none_data = []

    for code in none_code:
        url = get_url(code)
        count = 0
        print('========================start %s crawling========================' % code)
        while count < target_bundle_num:
            # 1페이지부터 12페이지를 한 묶음(bundle)으로 봄
            start_page = count * 12 + 1  # 1 page
            end_page = count * 12 + 12  # 12 page
            #requests를 통한 HTTP 요청
            try:
                for page in range(start_page, end_page + 1):
                    headers = {
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}
                    page_url = '{url}&page={page}'.format(url=url, page=page)
                    response = requests.get(page_url, headers=headers)

                    html = bs(response.text, "lxml")
                    html_table = html.select("table")   # BeautifulSoup 을 통해 html 페이지 내의 table 태그를 찾기

                    table = pd.read_html(str(html_table)) # html에서 찾은 table 태그를 pandas 로 읽어옴
                    df_day = table[0].dropna()
                    df = df.append(df_day)
            except:
                break
            count = count + 1
            time.sleep(random_time())  # Naver가 Crawling을 막아서 요청을 조금 느리게 해야함..

        print("Last Page : {}".format(page))
        print('\n수집한 데이터 수:',len(df))
        try:
            print('start date:', df['날짜'].iloc[-1], ' end date:', df['날짜'].iloc[0])
            df = preprocess_df  (df)     # preprocessing df

            tm = time.localtime()
            c_time = time.strftime('%m-%d_%I-%M-%S', tm)
            filename = str(code)+"_" + c_time + ".csv" # csv파일로 저장
            data_save(output_dir, filename, df)
        except:
            print('데이터 없음')
            none_data.append(code)
        print("========================End Crawling========================\n")

    # print(df.head())
    print("해당기간 데이터 없음:", none_data)

    return None

if __name__ == '__main__':
    main()
