import os
import pandas as pd

def merge_reason(df: pd.DataFrame,
                 reason_df: pd.DataFrame):
    
    df['in_reason'] = df.merge(reason_df,
                               left_on = 'in_reason_code',
                               right_on = 'code',
                               how = 'left')['reason']
    return df

def merge_address(df: pd.DataFrame,
                  add_df: pd.DataFrame):
    
    cols = {'short': ['in_area_short', 'out_area_short'],
            'long': ['in_area_long', 'out_area_long']} 
    add_col = {'short': 'add_short_code',
               'long': 'add_long_code'}

    for k, v in cols.items():
        if k == 'short':
            add_df_cp = add_df.iloc[:, :2].dropna()
        else:
            add_df_cp = add_df
            
        for col in v:
            in_out = col.split('_')[0]
            df[f'{in_out}_{k}_address'] = df.merge(add_df_cp,
                                                   left_on = col,
                                                   right_on = add_col[k],
                                                   how = 'left')[f'{k}_address']
    return df

def load_address():
    f_path = './data/populations/address.xlsx'
    df = pd.read_excel(f_path)
    # df['short_code'] = df['short_code'].astype('int')
    df['add_short_code'] = df['add_short_code'].loc[df['add_short_code'].notna(),].astype('int').astype('str')
    df['add_long_code'] = df['add_long_code'].astype('int').astype('str')
    # ·
    df['long_address'] = df['long_address'].str.replace('.', '·')
    return df

def load_dataset():
    dataset = dict()
    raw_list = os.listdir('./data/populations')
    
    # load address dataset that refers code book
    add_df = load_address()
    reason_df = pd.read_excel('./data/populations/reason_code.xlsx')
    
    """
    모든 feature들은 code임 -> 코드북 참고
    """
    columns = ['in_big_area', # 전입행정구역_시도코드
               'in_middle_area', # 전입행정구역_시군구코드
               'in_small_area',    # 전입행정구역_읍면동코드
               'out_big_area', # 전출행정구역_시도코드
               'out_middle_area', # 전출행정구역_시군구코드
               'out_small_area', # 전출행정구역_읍면동코드
               'in_reason_code', # 전입사유코드
               'in_year', # 전입연도
               'in_month' # 전입월 
               ]

    for i in range(1,11):
        # 전입자{i}_세대주관계코드, 전입자{i}_만연령
        columns.extend([f'in_peo{i}_headrel', f'in_peo{i}_age'])
    columns.append('household_code') # 세대 일련번호

    for r in raw_list:
        # print(r)
        r_path = os.path.join('./data/populations', r)
        if r.split('.')[1] == 'csv':
            print(r.split('.')[0])
            df = pd.read_csv(r_path, names=columns, header=None)
            # 세대별로 분석할 예정이니 세대원 데이터는 삭제한다
            df_1 = df.iloc[:, :9]
            df_2 = df.iloc[:, -1]
            df = df_1.join(df_2)
            # 전입행정구역_시군구
            df['in_area_short'] = df['in_big_area'].astype('str') +  df['in_middle_area'].astype('str')
            # 전출 행정구역_시군구
            df['out_area_short'] = df['out_big_area'].astype('str') +  df['out_middle_area'].astype('str')
            
            # 전입행정구역_시군구읍면동
            df['in_area_long'] =  df['in_area_short'] + df['in_small_area'].astype('str')
            # 전출 행정구역_시군구읍면동
            df['out_area_long'] = df['out_area_short'] +  df['out_small_area'].astype('str')
            
            dataset[r.split('.')[0]] = merge_address(df, add_df)
            dataset[r.split('.')[0]] = merge_reason(df, reason_df)
        else:
            pass
    return dataset            

def extract_out_in(year: str, df: pd.DataFrame):
    out_in = df.loc[df['out_area_short'] == '47230',] # 전출지를 영천시 기준으로
    out_in = out_in[out_in['in_area_short'] != '47230'] # 전입지 중 영천시 제외
    out_to_in_cnt = out_in.groupby('in_area_short')['in_area_short'].count()
    
    out_in_cnt_df = pd.DataFrame({
        "year": [year] * len(out_to_in_cnt),
        "src_area_short": ['47230'] * len(out_to_in_cnt),
        "tar_area_short": list(out_to_in_cnt.index),
        "cnt": list(out_to_in_cnt.values)
    })
    return out_in_cnt_df

def extract_reason(year: str, df: pd.DataFrame):
    out_in = df.loc[df['out_area_short'] == '47230',] # 전출지를 영천시 기준으로
    out_in = out_in[out_in['in_area_short'] != '47230'] # 전입지 중 영천시 제외
    
    out_in_re_res = out_in.groupby('in_reason')['in_reason'].count()
    
    out_in_re_res = pd.DataFrame({
        "year": [year] * len(out_in_re_res),
        "reason": out_in_re_res.index,
        "reason_count": out_in_re_res.values
    })
    
    return out_in_re_res

datasets = load_dataset()
df_22 = datasets['2022_population'].copy()

cols = ['in_area_short', 'in_short_address']
ext_22 = df_22.loc[:, cols].drop_duplicates(['in_area_short']).reset_index(drop=True)

out_in_cnt, out_in_year = list(), list()
for k, v in datasets.items():
    if k[0] == '2':
        out_in = v.loc[v['out_area_short'] == '47230',] # 전출지를 영천시 기준으로
        out_in = out_in[out_in['in_area_short'] != '47230'] # 전입지 중 영천시 제외
        out_in_cnt.append(len(out_in))
        out_in_year.append(k.split('_')[0])

df_out_in_trend = pd.DataFrame({
    "Year": out_in_year,
    "count": out_in_cnt
})

out_in_set = dict()
out_in_set_df = pd.DataFrame()
for k, v in datasets.items():
    if k[0] == '2':
        df = extract_out_in(k.split('_')[0],v)
        out_in_set_df = pd.concat([out_in_set_df, df])
    else:
        pass
out_in_set_df.to_csv('./preprocessed_dataset/2_out_cnt.csv', header=True, index=False)

# export reason
out_reason_df = pd.DataFrame()
for y in out_in_year:
    df = extract_reason(y, datasets[f'{y}_population'])
    out_reason_df = pd.concat([out_reason_df, df])
    # df.to_csv(f'../preprocessed_dataset/3_out_reason_{y}.csv', header=True, index=False)
# out_reason_df.to_csv('../preprocessed_dataset/3_out_reason.csv', header=True, index=False)