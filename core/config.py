data_path = './data/'
external_path = './external/'
model_path = './model/'
result_path = './results/'

# data_path = '~/2021-nh-bigdata-competition/data/'
# external_path = '~/2021-nh-bigdata-competition/external/'
# model_path = '~/2021-nh-bigdata-competition/model/'
# result_path = '~/2021-nh-bigdata-competition/results/'

train_df_name = 'train_data(final).csv'
##### Private Test시 data 폴더 내에 test file 넣은 후 test_df_name만 변경하면 됨
test_df_name = 'test_data(final).csv'

model_name = 'xgboost_final.json'

drop_features = ['act_id', 'iem_cd', 'bse_dt', 'iem_krl_nm']
used_features = ['byn_dt', 'high_mean', 'change_d', 'nsi', 'mean_amount',
       'volume_mean', 'mean_rank', 'volume_d', 'abs_change_mean', 'close_mean',
       'open_d', 'mean_stocks', 'mean_changesratio', 'open_mean', 'dollar',
       'gdp_rate', 'mean_marcap', 'low_mean', 'changesratio_d', 'amount_d',
       'marcap_d', 'stocks_d', 'rank_d', 'gdp', 'sex_dit_cd', 'cus_age_stn_cd',
       'ivs_icn_cd', 'cus_aet_stn_cd', 'mrz_pdt_tp_sgm_cd', 'lsg_sgm_cd',
       'tco_cus_grd_cd', 'tot_ivs_te_sgm_cd', 'mrz_btp_dit_cd', 'btp_cfc_cd',
       'mkt_pr_tal_scl_tp_cd', 'stk_dit_cd', 'iem_cd_te', 'bnc_qty',
       'tot_aet_amt', 'stk_par_pr', 'bnc_count', 'qty_change',
       'aet_amt_change', 'end_price', 'ivs_past_d_mean', 'past_d', 'hist_d']