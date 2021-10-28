#!/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.append('../')
import pandas as pd
import numpy as np
import core.config as conf

def mergeAll(df, train) :
    marcap_df = pd.read_csv(conf.external_path + 'result/mean_marcapdata.csv')
    marcap_df['code'] = marcap_df.apply(lambda x: 'A' + x['code'], axis=1)
    exchange_df = pd.read_csv(conf.external_path + 'result/exchange_rate.csv')
    nsi_df = pd.read_csv(conf.external_path + 'result/nsi_data.csv')
    stk_mean_df = pd.read_csv(conf.external_path + 'result/abs_mean_stockdata.csv')
    
    dtypes={'code':np.str, 'name':np.str,'open':np.int64, 'high':np.int64, 'low':np.int64, 'close':np.int64, 'volume':np.int64, 'amount':np.int64, 'changes':np.int64, 'changecode':np.str, 'changesratio':np.float64, 'marcap':np.int64, 'stocks':np.int64,'marketid':np.str, 'market':np.str, 'dept':np.str, 'rank':np.int64, 'date':np.int64}

    allmarcap_df = pd.read_csv(conf.external_path + 'result/all_marcap_data2016_2020.csv',dtype=dtypes)
    allmarcap_df = allmarcap_df.drop(['name','market','dept','marketid'],axis=1) # 1차 드롭
    allmarcap_df = allmarcap_df.drop(['close','changecode','changes','open','high','low','volume'],axis=1) # finance에서 들어간 것 drop

    allmarcap_df['code'] = allmarcap_df.apply(lambda x : 'A' + x['code'], axis = 1)
    allmarcap_df.columns = ['code','changesratio_d', 'amount_d', 'marcap_d', 'stocks_d', 'rank_d', 'date'] # 컬럼명 변경
    

    stk_mean_df['code'] = stk_mean_df.apply(lambda x : 'A' + x['code'], axis = 1)
    stk_mean_df = stk_mean_df.drop(['sq_abs_change','sq_abs_change100000'], axis=1)
    stk_mean_df.columns = ['code','open_mean', 'high_mean', 'low_mean', 'close_mean', 'volume_mean','abs_change_mean']

    df = pd.merge(left = df, right = stk_mean_df, how='left', left_on='iem_cd', right_on = 'code')
    df = df.drop('code', axis=1)
    
    df = MergeFinanceData(df)
    df = MergeMarcap(df, allmarcap_df)
    df = MergeMeanMarcap(df, marcap_df)
    df = MergeDollar(df, exchange_df)
    df = MergeGDP(df)
    df = MergeNSI(df, nsi_df)
    
    df = df.drop_duplicates()
    df = df.drop(['close_d', 'date', 'high_d', 'low_d'], axis = 1)
    # 최종 파일 저장
    if train :
        df.to_csv(conf.data_path + 'train_data(final).csv', index=False)
    else :
        df.to_csv(conf.data_path + 'test_data(final).csv', index=False)
    return df

# ==============================================================================================================
# 1. finance stock data - byn_dt 기준으로 open high low close volume change 추가
def MergeFinanceData(process_df):  #
    cd = process_df['iem_cd']
    date = process_df['byn_dt']

    di = conf.external_path + 'crawling/stockdata'
    file_list = os.listdir(di)

    f_list = []
    for i in cd:
        i = i[1:]
        f_name = list(filter(lambda x: i in x, file_list))
        if len(f_name) != 0:
            f_list.append(f_name)
        else:
            f_list.append(None)

    result = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Change'])
    for i in range(len(f_list)):
        if f_list[i] is not None:
            f = f_list[i][0]
            print(i, f)
            filepath = '{}/{}'.format(di, f)
            df = pd.read_csv(filepath)
            d = str(date[i])
            d = d[:4] + '-' + d[4:6] + '-' + d[6:]
            temp = df[df['Date'] == d]
            temp = temp.loc[:, ['Open', 'High', 'Low', 'Close', 'Volume', 'Change']]
            result = result.append(temp, ignore_index=True)
        else:
            result = result.append({'Open': 0, 'High': 0, 'Low': 0, 'Close': 0, 'Volume': 0, 'Change': 0},
                                   ignore_index=True)

    result.columns = ['open_d', 'high_d', 'low_d', 'close_d', 'volume_d', 'change_d']  # 열이름 변경
    process_df = pd.concat([process_df, result], axis=1)

    return process_df


# ==============================================================================================================
# 2. 그외 marcap mean data 추가 (mean_changesratio,  mean_amount, mean_marcap, mean_stocks, mean_rank)
def MergeMeanMarcap(process_df, marcap_df):
    process_df = pd.merge(left=process_df, right=marcap_df[
        {'code', 'mean_changesratio', 'mean_amount', 'mean_marcap', 'mean_stocks', 'mean_rank'}], how='left',
                          left_on='iem_cd', right_on='code')
    process_df = process_df.drop(['code'], axis=1)  # 중복열 제거

    return process_df


# ==============================================================================================================
# 3. dollar 추가 - byn_dt 기준으로 환율 추가
def MergeDollar(process_df, exchange_df):
    process_df = pd.merge(process_df, exchange_df, how='left', left_on='byn_dt', right_on='date')
    process_df = process_df.drop('date', axis=1)  # 중복열 제거

    return process_df


# ==============================================================================================================
# 4. gdp 추가 - 분기별 데이터 활용, 데이터를 직업 사용
def MergeGDP(process_df):
    conditions = [(process_df['byn_dt'] >= 20201001), (process_df['byn_dt'] >= 20200701),
                  (process_df['byn_dt'] >= 20200401), (process_df['byn_dt'] >= 20200101),
                  (process_df['byn_dt'] >= 20191001), (process_df['byn_dt'] >= 20190701),
                  (process_df['byn_dt'] >= 20190401), (process_df['byn_dt'] >= 20190101),
                  (process_df['byn_dt'] >= 20181001), (process_df['byn_dt'] >= 20180701),
                  (process_df['byn_dt'] >= 20180401), (process_df['byn_dt'] >= 20180101),
                  (process_df['byn_dt'] >= 20171001), (process_df['byn_dt'] >= 20170701),
                  (process_df['byn_dt'] >= 20170401), (process_df['byn_dt'] >= 20170101),
                  (process_df['byn_dt'] >= 20161001), (process_df['byn_dt'] >= 20160701),
                  (process_df['byn_dt'] >= 20160401), (process_df['byn_dt'] >= 20160101), ]
    choices1 = [1.1, 2.2, -3.2, -1.3, 2.3, 2.0, 2.1, 1.8, 3.1, 2.4, 3.1, 3.0,
                2.9, 3.9, 2.7, 3.1, 2.6, 2.8, 3.6, 2.8]
    process_df['gdp_rate'] = np.select(conditions, choices1, default=0)

    choices2 = [492100.10, 491181.50, 472328.10, 458202.40, 497064.80, 487177.00, 479907.00,
                454891.00, 489800.50, 485535.70, 473018.30, 449838.10, 475092.90, 473436.20,
                454141.70, 433027.30, 453412.40, 439421.60, 434462.90, 413482.60]
    process_df['gdp'] = np.select(conditions, choices2, default=0)

    return process_df


# ==============================================================================================================
# 5. nsi 추가
def MergeNSI(process_df, nsi_df):
    process_df = pd.merge(left=process_df, right=nsi_df, how='left', left_on='byn_dt', right_on='date')
    process_df.drop(['date'], axis=1)

    return process_df


# ==============================================================================================================
# 6. marcap_d추가
def MergeMarcap(process_df, allmarcap_df):
    process_df = pd.merge(left=process_df, right=allmarcap_df, how='left', left_on=['iem_cd', 'byn_dt'],
                          right_on=['code', 'date'])
    process_df = process_df.fillna(0)
    process_df = process_df.drop(['code', 'date'], axis=1)
    process_df = process_df.drop_duplicates()

    return process_df

