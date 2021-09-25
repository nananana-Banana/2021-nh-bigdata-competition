'''
https://financedata.github.io/posts/finance-data-reader-users-guide
한국 주식 가격, 미국주식 가격, 지수, 환율, 암호화폐 가격, 종목 리스팅 등 금융 데이터 수집 라이브러리
'''
import os
import FinanceDataReader as fdr
import pandas as pd

def get_data(code, s_date, e_date):
    # fdr.DataReader(종목코드, 시작일, 종료일)
    df = fdr.DataReader(code, s_date, e_date)

    return df

def data_save(output_dir, filename, dataset):
    path = os.path.join(output_dir, filename)
    dataset.to_csv(path)

def main():
    if os.path.exists("./stock_data"):
        output_dir = "./stock_data"
    else:
        os.mkdir("./stock_data")
        output_dir = "./stock_data"

    dataset = pd.DataFrame()
    none_data = []

    filepath = 'code.csv'
    code_file = pd.read_csv(filepath)
    code_list = code_file['iem_code'].str.strip()

    for i in range(len(code_list)):
        code = code_list[i]
        try:
            print(i, code)
            dataset = get_data(code, '20160104', '20201230')

            start_date = dataset.index[0]
            start_date = str(start_date).split()[0]
            end_date = dataset.index[-1]
            end_date = str(end_date).split()[0]

            filename = str(code) + "_" + str(start_date) + "_" + str(end_date) + ".csv"  # csv파일로 저장
            data_save(output_dir, filename, dataset)
        except:
            none_data.append(code)
            print(i, code, "정보 없음")
    print(none_data)
    return None

if __name__ == '__main__':
    main()
