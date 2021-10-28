#!/usr/bin/env python
# coding: utf-8
import os
import sys
sys.path.append('../../../../../')

import pandas as pd
import numpy as np
#import core.config as conf
from marcap.marcap_utils import marcap_data

# marcap 데이터를 불러와서 처리

dtypes={'Code':np.str, 'Name':np.str, 
          'Open':np.int64, 'High':np.int64, 'Low':np.int64, 'Close':np.int64, 'Volume':np.int64, 'Amount':np.int64,
          'Changes':np.int64, 'ChangeCode':np.str, 'ChagesRatio':np.float64, 'Marcap':np.int64, 'Stocks':np.int64,
          'MarketId':np.str, 'Market':np.str, 'Dept':np.str,
          'Rank':np.int64}
year = 2015
csv_file = 'marcap/data/marcap-%s.csv.gz' % (year)
df2015 = pd.read_csv(csv_file, dtype=dtypes)

year1 = 2016
csv_file = 'marcap/data/marcap-%s.csv.gz' % (year1)
df2016 = pd.read_csv(csv_file, dtype=dtypes)

year2 = 2017
csv_file = 'marcap/data/marcap-%s.csv.gz' % (year2)
df2017 = pd.read_csv(csv_file, dtype=dtypes)

year3 = 2018
csv_file = 'marcap/data/marcap-%s.csv.gz' % (year3)
df2018 = pd.read_csv(csv_file, dtype=dtypes)

year4 = 2019
csv_file = 'marcap/data/marcap-%s.csv.gz' % (year4)
df2019 = pd.read_csv(csv_file, dtype=dtypes)

year5 = 2020
csv_file = 'marcap/data/marcap-%s.csv.gz' % (year5)
df2020 = pd.read_csv(csv_file, dtype=dtypes)

all_df = pd.concat([df2016, df2017, df2018, df2018, df2020])

# 1. 종목으로 정렬 2. 날짜로 정렬
all_df = all_df.sort_values(by=['Code','Date'])

all_df.columns =['code','name','market','dept','close','changecode','changes','chagesratio','open','high','low','volume','amount','marcap','stocks','marketid','rank','date']

# 평균 내기 어려운 데이터는 삭제
# 'name', 'market', 'dept', 'changecode','marketid','date'
mean_df = all_df.drop(['name', 'market', 'dept', 'changecode','marketid','date'], axis=1)
mean_df['changes']=abs(mean_df['changes'])
mean_df['chagesratio']=abs(mean_df['chagesratio'])

# 종목별 평균
mean_df = mean_df.groupby(['code'], as_index=False).mean()

mean_df.columns =['code','mean_close','mean_changes','mean_chagesratio','mean_open','mean_high','mean_low','mean_volume','mean_amount','mean_marcap','mean_stocks','mean_rank']
mean_df.to_csv()

