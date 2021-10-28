import sys
sys.path.append('..')

import numpy as np
import pandas as pd
from tqdm import tqdm
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import swifter
import core.config as conf
from utils.preprocessing import *
from utils.merge_external_data import *

class XGBoost:
    def __init__(self):
        self.TARGET = 'hold_d'
    
    def preprocessing(self, df, train) :
        print('*********preprocessing...')
        
        ## 외부 데이터 불러오기
        ## 시간 관계상 미리 전처리 함
        #df = mergeAll(df, train)
        print("*********merge external data..")
        
        #cus info merge
        print("*********cus info merge..")
        cus_df = pd.read_csv(conf.data_path +'cus_info.csv')
        df = pd.merge(left = df, right = cus_df, how='left', on='act_id')
        iem_df = pd.read_csv(conf.data_path +'iem_info_20210902.csv')
        df = pd.merge(df, iem_df, how='left', on='iem_cd')
        
        #iem target encoding
        print("*********iem target encoding..")
        df = target_encoding(df, train)
        
        # from stk hist
        print("*********from stk hist..(bnc_count, qty_change, aet_amt_change, end_price")
        df = get_from_stk(df)
        
        #ivs_past_d 계산
        print("*********calculating ivs past_d..")
        df = apply_ivs_past_d(df) 
         
        # 4. past_d 계산
        print("*********calculating total past_d..")
        if train :
            df = cal_past_d(df)
            df['past_d'] = df.apply(lambda x : x['ivs_past_d_mean'] if x['past_d'] == 0 else x['past_d'], axis = 1)
        else :
            df = stk_past_d(df)
         
        # 5. hist_d 계산
        if train :
            print("*********calculating train hist_d..")
            holidays = get_holiday()
            df['hist_d'] = df.apply(lambda x : hist_d_half(x['byn_dt'], x['hold_d'], holidays), axis = 1)

        print("**preprocessing successfully")
        
        df['bnc_count'] = df['bnc_count'] + 1
        return df
    
    def train(self, valid = False):
        train_df = pd.read_csv(conf.data_path + conf.train_df_name)
        train_df = self.preprocessing(train_df, True)
        train_df = train_df.drop(conf.drop_features, axis = 1)
        train_df = train_df.fillna(0)
        col = train_df.columns.drop(self.TARGET)
        
        #if valid :
        X_train, X_valid, y_train, y_valid = train_test_split(train_df[col], train_df[self.TARGET], test_size = 0.2)
        #else :
        #    X_train = train_df[col]
        #    y_train = train_df[self.TARGET]
        print("**************")
        print(train_df.columns)
        model = xgb.XGBRegressor(eta = 0.1, n_estimators=1000, max_depth=8, subsample=0.7, colsample_bytree=0.8)
        print("===Training....===")
        model.fit(X_train, y_train, verbose=True)
        print("===Success===")
        model.save_model(conf.model_path + conf.model_name)
        print("===model saved..====")
        if valid :
            pred = model.predict(X_valid)
            score = np.sqrt(mean_squared_error(y_valid.values, np.round(pred)))
            print("Valid RMSE Score : ", score)
        return
    
    def predict(self):
        test_df = pd.read_csv(conf.data_path + conf.test_df_name)
        test_df = self.preprocessing(test_df, False)
        test_df = test_df[conf.used_features]
        test_df = test_df.fillna(0)
        test_df.to_csv('test_columns.csv', index = False)
        model = xgb.XGBRegressor()
        model.load_model(conf.model_path + conf.model_name)
        submission = pd.read_csv(conf.data_path+"sample_submission.csv")
        print("===Predict...===")
        print(test_df.columns)
        y_pred = model.predict(test_df)
        print("===Success===")
        test_df['y_pred'] = y_pred
        y_pred = test_df.apply(lambda x : x['y_pred'] if x['y_pred'] <= x['hist_d']+146 else x['hist_d']+146, axis = 1)
        result = []
        for i in y_pred:
            if i < 0 :
                i = 1
            result.append(i)
        submission["hold_d"] = np.round(result)
        submission.to_csv(conf.result_path + "stk_hld_test.csv", index = False)
        print("===Submission File saved===")
        return