# 외부데이터 수집 및 활용 방안
## 1. 주식 데이터 
#### 1) [FinanceDataReader](https://financedata.github.io/posts/finance-data-reader-users-guide) 를 활용한 데이터 수집
file: finance_stock_data.py

FinanceDataReader는 한국 주식 가격, 미국주식 가격, 지수, 환율, 암호화폐 가격, 종목 리스팅 등 금융 데이터를 수집에 사용되는 라이브러리로 
`code.csv`에 있는 3079개 종목의 2016년-2020년 데이터를 수집함.
그결과 2812개 데이터를 수집할 수 있었음.

FinanceDataReader에서 정보를 가져오지 못한 267개 종목은 네이버 주식 사이트에서 크롤링을 시도했으나, 
데이터가 존재하지 않거나, 2016년-2020년 데이터가 없는 종목이었음.
266개 종목에 대한 내용은 `none_data.csv`에서 확인 가능하며, 네이버 주식 데이터 수집 내용은 `output_log.txt` 참고하면 됨.
