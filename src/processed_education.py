import os
import pandas as pd

def load_school():
    region = ['daegu', 'kb']
    encode_format = ['cp949', 'utf-8']

    sch_dataset = dict()
    r_path = './data'
    for reg, enc in zip(region, encode_format):
        f_path = os.path.join(r_path, 
                            f'{reg}_school_2024.csv')
        sch_dataset[reg] = pd.read_csv(f_path, 
                                    encoding=enc).iloc[:, :3]
    return sch_dataset

def school_class(school_name: str):
    cl_school = ['유치원', '초등학교', '중학교', '고등학교']
    
    return next((level 
                 for level in cl_school 
                 if level in school_name), '각종학교')

def region_school_cnt(state: str,
                      region: str,
                      tar_col: str,
                      df:pd.DataFrame):
    
    g_df =  df.groupby(tar_col)[tar_col].count()
    
    return pd.DataFrame({
        'state': [state] * len(g_df),
        'region': [region] * len(g_df), 
        'school_lavel': list(g_df.index),
        'number_of_school': list(g_df.values)
    })

# task
# count the # of shool by each region

sh_dataset = load_school()

daegu_sch = sh_dataset['daegu'].copy()
daegu_sch['class'] = daegu_sch['학교명'].apply(school_class) 
# daegu_sch.loc[daegu_sch['class'].isna(), ]

r_path = './preprocessed_dataset'

daegu_reg_school_count = pd.DataFrame()
reg_li = daegu_sch['관할구군청'].unique()

# duplicated code -> it needs to refactoring
for reg in reg_li:
    reg_ext = daegu_sch.loc[daegu_sch['관할구군청'] == reg, ]
    reg_ext = region_school_cnt('대구광역시', reg, 'class', reg_ext)
    daegu_reg_school_count = pd.concat([daegu_reg_school_count, reg_ext])
daegu_reg_school_count = daegu_reg_school_count.reset_index(drop=True)

kb_sch = sh_dataset['kb'].copy()
kb_sch['class'] = kb_sch['학교(유치원)명'].apply(school_class)

kb_reg_school_count = pd.DataFrame()
reg_li = kb_sch['시군명'].unique()

for reg in reg_li:
    reg_ext = kb_sch.loc[kb_sch['시군명'] == reg, ]
    reg_ext = region_school_cnt('경상북도', reg, 'class', reg_ext)
    kb_reg_school_count = pd.concat([kb_reg_school_count, reg_ext])
kb_reg_school_count = kb_reg_school_count.reset_index(drop=True)

reg_school_count = pd.concat([daegu_reg_school_count, kb_reg_school_count])
reg_school_count = reg_school_count.reset_index(drop=True)

# f_path = os.path.join(r_path, '4_school.csv')
# reg_school_count.to_csv(f_path, index=False)