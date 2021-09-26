# 외부데이터 수집 및 활용 방안

## 1. 주식 데이터 크롤링

####  1) iem_info data 전처리
 `./crawling/iem_to_code.py`

3079개 종목 코드 맨 앞 알파벳을 제외한 6자리 숫자 형태로 가공

코드 데이터: `./crawling/codedata/code.csv`
  

#### 2) [FinanceDataReader](https://financedata.github.io/posts/finance-data-reader-users-guide) 를 활용한 데이터 수집

`./crawling/finance_stock_data.py`

FinanceDataReader는 한국 주식 가격, 미국주식 가격, 지수, 환율, 암호화폐 가격, 종목 리스팅 등 금융 데이터를 수집에 사용되는 라이브러리로 
`./crawling/codedata/code.csv`에 있는 3079개 종목의 2016년 - 2020년 데이터를 수집함.
그 결과 **2812개** 종목 데이터를 수집할 수 있었음. 

수집한 종목 데이터: `  ./crawling/stockdata/stockdata.zip`
  
#### 3) Naver crawling data
`./crawling/naver_stock_crawling.py`

FinanceDataReader에서 정보를 가져오지 못한 **267개** 종목은 네이버 주식 사이트에서 크롤링을 시도했으나, 
데이터가 존재하지 않거나, 2016년-2020년 데이터가 없는 종목이었음.

정보가 없는 종목 코드: `./crawling/codedata/none_code.csv`

네이버 주식 데이터 수집 로그: `./crawling/naver_stock_crawling_log.txt`

2812개 데이터의 평균 정보: `./result/mean_stockdata.csv`

#### reference
https://financedata.github.io<br>
https://github.com/Se-Hun/StockPrediction