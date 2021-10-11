data_path = '~/2021-nh-bigdata-competition/data/'
external_path = '~/2021-nh-bigdata-competition/external/result/'
model_path = '~/2021-nh-bigdata-competition/model/'
result_path = '~/2021-nh-bigdata-competition/results/'

#train_df_name = 'train_data(new_past_d,new_stk_data, new_external_data(marcap), nsi).csv'
train_df_name = 'stk_hld_train.csv'
#test_df_name = 'test_data(new_past_d,new_stk_data, new_external_data(marcap), nsi).csv'
test_df_name = 'stk_hld_test.csv'
model_name = 'xgboost_final.json'

#drop_features = ['act_id', 'iem_cd','date']
drop_features = ['act_id', 'iem_cd', 'iem_krl_nm', 'bse_dt']
used_features = ['byn_dt', 'past_d', 'sex_dit_cd',
       'cus_age_stn_cd', 'ivs_icn_cd', 'cus_aet_stn_cd', 'mrz_pdt_tp_sgm_cd',
       'lsg_sgm_cd', 'tco_cus_grd_cd', 'tot_ivs_te_sgm_cd', 'mrz_btp_dit_cd',
       'btp_cfc_cd', 'mkt_pr_tal_scl_tp_cd', 'stk_dit_cd',
       'hist_d', 'iem_cd_te', 'ivs_past_d_mean', 'bnc_qty', 'tot_aet_amt',
       'stk_par_pr', 'end_price', 'bnc_count', 'qty_change', 'aet_amt_change',
       'open_d', 'volume_d', 'change_d', 'nsi', 'dollar', 'mean_changesratio',
       'mean_amount', 'mean_marcap', 'mean_stocks', 'mean_rank', 'gdp_rate',
       'open_mean', 'high_mean', 'low_mean', 'close_mean', 'volume_mean',
       'abs_change_mean']


#self.xgb_parms = [n_estimators=1000, max_depth=8, subsample=0.7, colsample_bytree=0.8]