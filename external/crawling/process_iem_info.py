import pandas as pd
import sys
import os

def main():
    filepath = '../data/iem_info_20210902.csv'
    iem_df = pd.read_csv(filepath)

    iem_codes = iem_df['iem_cd'].str.strip()

    result = []
    for i in iem_codes:
        result.append(i[1:])

    data = pd.DataFrame(result, columns=['iem_code'])
    data.to_csv('code.csv', index=False)

if __name__ == '__main__':
    main()
