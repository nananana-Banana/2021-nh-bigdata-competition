#!/usr/bin/env python
# coding: utf-8
import os, sys
import numpy as np
import pandas as pd

di = './crawling/stockdata'
file_list = os.listdir(di)

code_list = []
for i in file_list:
    code_list.append(i[:6])

# ## 전체 평균 구하기
# column - Date,Open,High,Low,Close,Volume,Change
result = []
for i in file_list:
    filepath = '{}/{}'.format(di, i)
    df = pd.read_csv(filepath)
    df = df.iloc[:,1:] # 날짜 제외하고 가져오기
    mean_list = list(df.mean())# 평균 구하기
    result. append(mean_list)

filepath = '{}/{}'.format(di, i)
df = pd.read_csv(filepath)

resultdf = pd.DataFrame(result, columns=['open','high','low','close','volume','change'])
resultdf.head(10)

resultdf.insert(0,'code',code_list)
resultdf.head(10)

# output_path = './result/mean_stockdata.csv'
# resultdf.to_csv(output_path,index = False)  # 파일저장


# ## 전체 평균 구하기 (change 절대값 처리)
# column - Date,Open,High,Low,Close,Volume,Change
result2 = []
change_mean = []
for i in file_list:
    filepath = '{}/{}'.format(di, i)
    df2 = pd.read_csv(filepath)
    change_list = df2.iloc[:, 6].abs() # change 절대값 
    change_mean.append(change_list.mean()) # 절대값들의 평균

    df2 = df2.iloc[:,1:6] # 날짜, change 제외하고 가져오기
    mean_list = np.array(df2.mean())# 평균 구하기
    print(mean_list)
    result2.append(list(mean_list))

resultdf2 = pd.DataFrame(result2, columns=['open','high','low','close','volume'])
resultdf2.head(10)

resultdf2['abs_change'] = change_mean
resultdf2['sq_abs_change'] = resultdf2['abs_change']**2 # 사용안하는 컬럼
resultdf2['sq_abs_change100000'] = resultdf2['sq_abs_change']*100000 # 사용안하는 컬럼

resultdf2.insert(0,'code',code_list) # 코드 추가

output_path = './result/var_stockdata.csv'
resultdf2.to_csv(output_path,index = False)


# 년도별 평균 구하기
# column - Date,Open,High,Low,Close,Volume,Change
result = []
change_mean = []
for i in file_list:
    filepath = '{}/{}'.format(di, i)
    df = pd.read_csv(filepath)
    df = df[df.Date.str.contains(r'2016')] #2016 데이터만 가져오기

    change_list = df.iloc[:, 6].abs() # change 절대값 
    change_mean.append(change_list.mean()) # 절대값들의 평균

    if len(df) != 0:
        df = df.iloc[:,1:6] # 날짜, change 제외하고 가져오기
        mean_list = np.array(df.mean())# 평균 구하기
        result.append(list(mean_list))
    else:
        result.append([0,0,0,0,0])

resultdf = pd.DataFrame(result, columns=['open','high','low','close','volume'])
resultdf.head(10)

resultdf['abs_change'] = change_mean
resultdf.head(10)

resultdf.insert(0,'code',code_list)
resultdf.head(10)


output_path = './result/mean_stock2016.csv'
resultdf.to_csv(output_path,index = False)