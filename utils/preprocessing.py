import os
import sys
sys.path.append('../')
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from category_encoders import TargetEncoder
import pickle
import core.config as conf
from tqdm import tqdm

def get_holiday():
    holiday = pd.read_csv(conf.external_path +'holiday_date.csv')

    holidays = pd.to_datetime(holiday['date'], infer_datetime_format=True).dt.strftime("%Y-%m-%d")
    holidays = list(holidays)
    for i in range(len(holidays)):
        tmp = holidays[i].split('-')
        holidays[i] = ''.join(tmp)
    holidays = list(map(int, holidays))
    return holidays

def working_day(s_dt, e_dt, holidays) : # 공휴일 제외 # 공휴일이 주말인 경우 고려 
    count = 0
    for day in holidays:
        if day >= s_dt and day <= e_dt:
                count += 1
        elif day > e_dt:
                break
        else:
                continue
    s_dt = str(s_dt).split('.')[0]
    e_dt = str(e_dt).split('.')[0]
    s_dt = s_dt[:4] + '-' + s_dt[4:6] + '-' + s_dt[6:]
    e_dt = e_dt[:4] + '-' + e_dt[4:6] + '-' + e_dt[6:]
    w_day = np.busday_count(s_dt, e_dt, weekmask='1111100') # 주말제외

    result = w_day - count
    return result

def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

def hist_d_half(buy, hold_d, holidays) :
    buy_d = str(buy)
    buy_d = datetime(int(buy_d[:4]), int(buy_d[4:6]), int(buy_d[6:]))
    sell = to_integer(buy_d+timedelta(days=hold_d))
    base = [20160101, 20160630, 20170102, 20170630, 20180102, 20180630, 
            20190102, 20190630, 20200102, 20200630, 20210101]

    for i in range(len(base)) :
        if sell < base[i] :
            if buy > base[i-1] :
                return hold_d*0.6
                #return working_day(buy, base[i])
            else :
                return working_day(buy, base[i-1], holidays)

def target_encoding(df, train) :
    if train : 
        target_encoder = TargetEncoder()
        target_encoder.fit(df['iem_cd'], df['hold_d'])
        df['iem_cd_te'] = target_encoder.transform(df['iem_cd'])
        with open('./data/preprocessing/' + 'iem_te.pkl', 'wb') as f:
            pickle.dump(target_encoder, f)
    else :
        with open('./data/preprocessing/' + 'iem_te.pkl', 'rb') as f:
            target_encoder = pickle.load(f)
        df['iem_cd_te'] = target_encoder.transform(df['iem_cd'])
    return df

def cal_past_d(df) :
    df['past_d'] = 0
    df = df.sort_values(by = ['act_id', 'iem_cd', 'byn_dt'], axis = 0).reset_index(drop=True)
    iem = ''
    cnt = 1
    print('past_d calculating...')
    for idx, row in df.iterrows() :
        if row['iem_cd'] != iem :
            iem = row['iem_cd']
            cnt = 1
        else :
            df.at[idx, 'past_d'] = (df.iloc[idx-1]['past_d']*(cnt-1) + df.iloc[idx-1]['hold_d']) / cnt
            cnt += 1
    return df

def stk_hist(act_id, iem_cd) :
    diff_date = []
    s_dt = 0
    tmp_df = stk_df[stk_df['act_id']==act_id][stk_df['iem_cd']==iem_cd][['bse_dt', 'bnc_qty']]
    if len(tmp_df) == 0 : return None

    sell = tmp_df[tmp_df['bnc_qty']==0.0]#매도
    trade = tmp_df[tmp_df['bnc_qty']!=0.0]#매매
    
    if len(sell) == 0 : # 판 기록이 없을 때
        t_dt = trade['bse_dt'].values[0]
        diff_date.append(working_day(t_dt, 20201231))
    elif len(trade) == 0 : # 산 기록이 없을 때
        s_dt = sell['bse_dt'].values[0]
        diff_date.append(working_day(20160101, s_dt))
    else : 
        for _, row in sell.iterrows() :
            s_dt = row['bse_dt']
            t_dt = trade[trade['bse_dt'] <= s_dt]['bse_dt'].values[0]
            trade = trade[trade['bse_dt'] > t_dt]
            diff_date.append(working_day(t_dt, s_dt))
        trade = trade[trade['bse_dt']>s_dt]
        if len(trade) != 0 :
            t_dt = trade['bse_dt'].values[0]
            diff_date.append(working_day(t_dt, 20201231))    
    return np.mean(diff_date)

def cal_duration(act_id, hist):
    df = hist[(hist['act_id'] == act_id)][['act_id', 'iem_cd', 'bse_dt', 'bnc_qty', 'tot_aet_amt', 'ivs_icn_cd']]
    sorted_df = df.sort_values(by=['iem_cd', 'bse_dt'], ascending = [True, True])
    sorted_df = sorted_df.reset_index(drop = True)
    sorted_df['past_d'] = 0
    cur_dur = {}
    #     dur_list = []
    for i in range(len(sorted_df)):    
        # 위에서부터 하나씩 읽어가는데 딕셔너리에 종목코드가 존재하지 않는다면 해당 날짜 추가
        if sorted_df['iem_cd'][i] not in cur_dur:
            if sorted_df['bnc_qty'][i] == 0 :
                sell = sorted_df['bse_dt'][i]
                buy = 20160102
                sorted_df['past_d'][i] = working_day(buy-sell)
            cur_dur[sorted_df['iem_cd'][i]] = sorted_df['bse_dt'][i]
            
        # 이미 존재하면 해당 잔고가 0인지 확인
        else :
            # 일단 보유기간은 사고/팔고 개념이 있으니깐 팔지 않은(0이 아닌) 주식은 계산 X
            # 해당 잔고가 0이면 그 날짜와 딕셔너리에 존재하는 날짜를 사용해 보유 기간 계산
            # 어떤 종목을 다 팔고 다시 사고/팔았을 경우도 생각
            if sorted_df['bnc_qty'][i] == 0:
                sell = sorted_df['bse_dt'][i]
                buy = cur_dur[sorted_df['iem_cd'][i]]
                dur = working_day(buy, sell)
                sorted_df['past_d'][i] = dur 
                # 다 팔았으니깐 딕셔너리에서 해당 종목코드 삭제(나중에 다시 살 경우 대비)
                del cur_dur[sorted_df['iem_cd'][i]]
            # 0이 없다: 다 팔지 않음 ==> 일단 보유기간 측정 안하는 걸로.
            else:
                continue
    last_day = 20201231
    for i in cur_dur.items() :
        past_d = working_day(i[1], last_day)
        sorted_df = sorted_df.append({'act_id' : act_id , 'iem_cd' : i[0], 'bse_dt' : last_day, 'bnc_qty' : 0, 'tot_aet_amt' : 0, 'past_d' : past_d} , ignore_index=True)
        
    return sorted_df

def cal_hist() :
    hist = pd.read_csv(conf.data_path + 'stk_bnc_hist.csv')
    cus = pd.read_csv(conf.data_path + 'cus_info.csv')
    hist = pd.merge(hist, cus[['act_id', 'ivs_icn_cd']], how='left', on = 'act_id')
    ivs_lst = sorted(hist['ivs_icn_cd'].unique())
    df_lst = [0] * len(ivs_lst)
    
    for i in range(len(ivs_lst)) :
        ivs_code = ivs_lst[i]
        df = hist[hist['ivs_icn_cd'] == ivs_code]
        id_list = df['act_id'].unique()
        for j in range(len(id_list)):
            if j == 0:
                act_id = id_list[j]
                tmp_df1 = cal_duration(act_id, hist)
            else:
                act_id = id_list[j]
                tmp_df2 = cal_duration(act_id, hist)
                tmp_df1 = pd.concat([tmp_df1, tmp_df2], axis = 0)
        tmp_df1.reset_index(drop = True)
        df_lst[i] = tmp_df1
    return df_lst

def chk_ivs_past_d() :
    if os.path.exists('./data/preprocessing/ivs_past_d_mean.csv') :
        print("ivs_past_d_mean file is already.")
        return
    print("make ivs_past_d mean file")
    ivs_lst, df_lst = cal_hist()
    for i in range(len(ivs_lst)) :
        if i == 0 :
            df1 = df_lst[i].reset_index(drop=True)
            df1 = df1[(df1['past_d']) != 0]
            df1 = df1.groupby(['iem_cd'])['past_d'].mean().reset_index(name='ivs_past_d_mean')
            df1['ivs_icn_cd'] = ivs_lst[i]
        else :
            df2 = df_lst[i].reset_index(drop=True)
            df2 = df2[(df2['past_d']) != 0]
            df2 = df2.groupby(['iem_cd'])['past_d'].mean().reset_index(name='ivs_past_d_mean')
            df2['ivs_icn_cd'] = ivs_lst[i]
            df1 = pd.concat([df1, df2], axis = 0)
    df1.to_csv(conf.data_path + 'preprocessing/' + 'ivs_past_d_mean.csv', index= False)

def apply_ivs_past_d(df) :
    chk_ivs_past_d()
    ivs_past_df = pd.read_csv(conf.data_path + 'preprocessing/' + 'ivs_past_d_mean.csv')
    print(df.columns)
    df = pd.merge(df, ivs_past_df, how = 'left', on = ['iem_cd', 'ivs_icn_cd'])
    return df

def bnc_count(hist):
    hist = hist
    tmp = hist.groupby(['act_id', 'iem_cd'])['bse_dt'].count().reset_index(name='bnc_count')
    tmp = pd.merge(hist, tmp, how = 'left', on = ['act_id', 'iem_cd'])
    return tmp

def qty_change(hist):
    hist = hist
    sorted_hist = hist.sort_values(by=['iem_cd', 'bse_dt'], ascending = [True, True])
    sorted_hist = sorted_hist.reset_index(drop=True)
    sorted_hist = sorted_hist.groupby(['act_id', 'iem_cd'])['bnc_qty'].apply(list).reset_index(name = 'qty_list')
    sorted_hist['qty_change'] = 0
    
    for i in range(len(sorted_hist)):
        qty_change = []
        tmp = sorted_hist['qty_list'][i]

        for j in range(len(tmp)-1):
            change = abs(tmp[j+1] - tmp[j])
            qty_change.append(change)

        qty_change = np.array(qty_change)
        qty_mean = np.mean(qty_change)
        sorted_hist['qty_change'][i] = qty_mean
        
    sorted_hist = sorted_hist.drop(['qty_list'], axis = 1)
    
    # stk_bnc_hist 데이터와 merge
    new_hist = pd.merge(hist, sorted_hist, how = 'left', on = ['act_id', 'iem_cd'])
    
    
    return new_hist

def aet_amt_change(hist):
    hist = hist
    sorted_hist = hist.sort_values(by=['iem_cd', 'bse_dt'], ascending = [True, True])
    sorted_hist = sorted_hist.reset_index(drop=True)
    sorted_hist = sorted_hist.groupby(['act_id', 'iem_cd'])['tot_aet_amt'].apply(list).reset_index(name = 'aet_amt_list')
    sorted_hist['aet_amt_change'] = 0
    
    for i in range(len(sorted_hist)):
        aet_change = []
        tmp = sorted_hist['aet_amt_list'][i]
        for j in range(len(tmp)-1):
            change = abs(tmp[j+1] - tmp[j])
            aet_change.append(change)
        aet_change = np.array(aet_change)
        aet_mean = np.mean(aet_change)

        sorted_hist['aet_amt_change'][i] = aet_mean
        
    sorted_hist = sorted_hist.drop(['aet_amt_list'], axis = 1)
    
    # stk_bnc_hist 데이터와 merge
    new_hist = pd.merge(hist, sorted_hist, how = 'left', on = ['act_id', 'iem_cd'])
    
    return new_hist

def end_price(hist):
    new_hist = hist
    new_hist['end_price'] = 0
    
    for i in range(len(new_hist)):
        tot = new_hist['tot_aet_amt'][i]
        qty = new_hist['bnc_qty'][i]
        end_price = tot // qty
        new_hist['end_price'][i] = end_price
    
    return new_hist

def get_from_stk(df) :
    hist = pd.read_csv(conf.data_path + 'stk_bnc_hist.csv')
    new_hist = bnc_count(hist)
    new_hist = qty_change(new_hist)
    new_hist = aet_amt_change(new_hist)
    new_hist = end_price(new_hist)
    df = pd.merge(df, new_hist, how='left', left_on = ['act_id', 'iem_cd', 'byn_dt'], right_on = ['act_id', 'iem_cd', 'bse_dt'])
    return df