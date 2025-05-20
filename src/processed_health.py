import os
import pandas as pd

def load_dataset():
    r_path = './data/health'
    f_list = os.listdir(r_path)
    
    datasets = dict()
    for f in f_list:
        f_path = os.path.join(r_path, f)
        f_name = f.split('.')[0].split('_')[0]
        datasets[f_name] = pd.read_csv(f_path, encoding='cp949')
        print(f_name)
    return datasets
    
def processing_cnt(state: str,
                   reg_col_name: str,
                   target_col_name: str,
                   df: pd.DataFrame):
    
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
    
# task
# count the # of hospital in each region
datasets = load_dataset()

h_daegu = datasets['daegu'].copy()
h_kb = datasets['kb'].copy()

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

# preprocessing about kb 
target_re = ['포항시 북구', '포항시 남구']
for t in target_re:
    h_kb['시군명'] = h_kb['시군명'].str.replace(t, '포항시')

h_kb = processing_cnt(state = '경상북도',
                      reg_col_name = '시군명',
                      target_col_name='종류',
                      df = h_kb)

concated_data = pd.concat([h_daegu, h_kb])
concated_data.to_csv('./preprocessed_dataset/5_hospital.csv', header=True, index=False)

# discard_cat = [cat for cat in cat_da if cat not in cat_kb]