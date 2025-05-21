import os
import pandas as pd
from src.load_dataset import load_datasets

def processing_cnt(state: str,
                   reg_col_name: str,
                   target_col_name: str,
                   df: pd.DataFrame) -> pd.DataFrame:
    
    concated_df = pd.DataFrame()
    reg_li = df[reg_col_name].unique()
    
    for reg in reg_li:
        reg_ext = df.loc[df[reg_col_name] == reg, ]
        reg_ext = reg_ext.groupby(target_col_name)[target_col_name].count()
        reg_ext = pd.DataFrame({
            'state': [state] * len(reg_ext),
            'region': [reg] * len(reg_ext),
            'cat_hospital': list(reg_ext.index),
            'number_of_hospital': list(reg_ext.values)
        })
        concated_df = pd.concat([concated_df, reg_ext])
        concated_df = concated_df.reset_index(drop=True)
    return concated_df

def convert_pivot_table(df: pd.DataFrame, 
                        state: str,
                        tar_cat_col: str,
                        tar_cnt_col: str) -> pd.DataFrame:
    
    df = df.pivot_table(index=['region'],
                        columns=tar_cat_col,
                        values=tar_cnt_col,
                        fill_value=0).astype('int')
    df = df.reset_index().rename_axis(None, axis=1)
    df['state'] = pd.Series([state]*len(df))
    df_state_pop = df.pop('state')
    df.insert(0, 'state', df_state_pop)
    
    return df
    
# task
# count the # of hospital in each region
datasets = load_datasets('health')

h_daegu = datasets['daegu_health_2024'].copy()
h_kb = datasets['kb_heal_2024'].copy()

# preprocessing about Daegu
h_daegu = h_daegu.drop('연번', axis=1)
cat_da = h_daegu['종별'].unique()
cat_kb = h_kb['종류'].unique()

relatives = [cat for cat in cat_da if cat not in cat_kb]
h_daegu = h_daegu.drop(h_daegu.loc[h_daegu['종별'].isin(relatives),].index).reset_index(drop=True)

h_daegu['구군'] = h_daegu['구군'].str.extract(r'([가-힇]+)')
h_daegu = h_daegu.iloc[:, [0,2]]

h_daegu = processing_cnt(state='대구광역시',
                         reg_col_name='구군',
                         target_col_name='종별',
                         df = h_daegu)
# df_pivot = df.pivot_table(index='이름', columns='영화장르', values='관람횟수', fill_value=0)
h_daegu = convert_pivot_table(h_daegu,
                              '대구광역시',
                              'cat_hospital',
                              'number_of_hospital') 

target_re = ['포항시 북구', '포항시 남구']
for t in target_re:
    h_kb['시군명'] = h_kb['시군명'].str.replace(t, '포항시')

h_kb = processing_cnt(state = '경상북도',
                      reg_col_name = '시군명',
                      target_col_name='종류',
                      df = h_kb)
h_kb = convert_pivot_table(df = h_kb,
                           state='경상북도',
                           tar_cat_col='cat_hospital', 
                           tar_cnt_col='number_of_hospital')

culture_processed = pd.read_csv('./preprocessed_dataset/society_df.csv')

culture_processed['state'] = culture_processed['행정구역'].apply(lambda x: x.split('_')[0])
culture_processed['region'] = culture_processed['행정구역'].apply(lambda x: x.split('_')[1])
culture_processed = culture_processed.iloc[:, 1:]
filt_region = list(culture_processed['region'].unique())

concated_data = pd.concat([h_daegu, h_kb]).reset_index(drop=True)
concated_data = concated_data.loc[concated_data['region'].isin(filt_region) == True, :]

concated_data.to_csv('./preprocessed_dataset/5_hospital.csv', header=True, index=False)

# discard_cat = [cat for cat in cat_da if cat not in cat_kb]