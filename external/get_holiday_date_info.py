#!/usr/bin/env python
# coding: utf-8

# # 한국천문연구원_특일 정보
# 공휴일 정보 api를 활용한 공휴일 데이터 수집
# 매수일과 보유기간을 활용한 매도일 계산에 공휴일 정보가 필요하여 수집.
# 
# 공공데이터포털 API 활용신청
# https://www.data.go.kr/iim/api/selectAPIAcountView.do
# 
#     
# 서비스 URL: http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/{서비스오퍼레이션}
#  
# <서비스 종류><br> 
# 국경일 정보: getHoliDeInfo<Br>
# 공휴일 정보: getRestDeInfo<br>
# 기념일 정보: getAnniversaryInfo
#     
# <호출 파라미터>   
# 서비스키(공공포털에서 받은 인증키): ServiceKey<br>
# 페이지 번호: pageNo<br>
# 한 페이지 결과 수: numOfRows<br>
# 년도: solYear<br>
# 월: solMonth<br>
#     
# ### 태그 설명<br>
# dateKine 종류<br>
# -01: 국경일(설날, 어린이날, 광복절)<br>
# -02: 기념일(의병의 날, 정보보호의 날, 4/19 혁명 기념일)<br>
# -03: 24절기(청명, 경칩, 하지)<br>
# -04: 잡절(단오, 한식)<br>
#     
# dateName 명칭<br>
# 
# isHoliday 공공기환 휴일 여부<br>
# 
# locdate 날짜<br>
# 
# seq 순번<br>

import requests
from urllib import parse
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

def GetHoliday(year: int) -> pd.DataFrame:
    url= "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/"
    api_key_utf8 = "RUAtvomINtNMTEkyJK47WUcb8pKw5B%2F1x7jnaj5B%2BbXwXOAzZbsCp%2BpmaYqQ4prnMDkCSCYrFF4uD4OXrMuHjQ%3D%3D"
    api_key_decode = parse.unquote(api_key_utf8)

    url_holiday = url + "getRestDeInfo"
    params = {
        "ServiceKey" : api_key_decode,
        "solYear": year, # 요청 년도
        "numOfRows": 100
    }

    response = requests.get(url_holiday, params=params)
    xml = BeautifulSoup(response.text, 'lxml')
    items = xml.find('items')
    item_list = []
    for i in items:
        i_dict = {
            "holiday": i.find("datename").text.strip(),
            "date": datetime.strptime(i.find("locdate").text.strip(), '%Y%m%d')
        }
        item_list.append(i_dict)
    return pd.DataFrame(item_list)

totaldf = pd.DataFrame(columns=['holiday','date'])
for i in range(2016,2021):
    d = GetHoliday(i)
    totaldf = pd.concat([totaldf, d], ignore_index=True)

output_path = '../result/holiday_date.csv'
totaldf.to_csv(output_path, index = False)

