import pandas as pd
import warnings
from src.load_dataset import load_datasets

from numpy import nan
warnings.filterwarnings('ignore')

def split_state_region(df: pd.DataFrame,  
                       target_column: str) -> pd.DataFrame:
    df['state'] = df[target_column].apply(lambda x: x.split(' ')[0])
    df['region'] = df[target_column].apply(lambda x: x.split(' ')[1])
    df = df.drop(columns=[target_column])
    return df

def convert_count_df(df: pd.DataFrame,
                    target_col: str,
                    state: str,
                    category: str) -> pd.DataFrame:
    ds = df.groupby(target_col)[target_col].count()
    
    return pd.DataFrame({
        'state': [state] * len(ds),
        'region': list(ds.index),
        f'num_{category}': list(ds.values)
    })
    
def concat_all(df: pd.DataFrame,
               address_col: str,
               category: str) -> pd.DataFrame:
    states = {'daegu': '대구광역시', 'kb': '경상북도'}

    processed_dict = dict()
    for e, k in states.items():
        processed_df = df.loc[df[address_col].str.contains(k) == True,].reset_index()
        processed_df = split_state_region(processed_df, address_col)
        processed_dict[e] = convert_count_df(processed_df, 'region', k, category) 
    
    concated_df = pd.concat([processed_dict['daegu'], processed_dict['kb']])
        
    return concated_df.reset_index(drop=True)

datasets = load_datasets(category='cultures')

parks = datasets['parks'].copy()
parks = parks[parks['공원구분'] != '어린이공원'].reset_index(drop=True)

address_col = '소재지지번주소'
parks = concat_all(parks,
                   address_col,
                   'parks')

culture_processed = pd.read_csv('./preprocessed_dataset/society_df.csv')
culture_processed['state'] = culture_processed['행정구역'].apply(lambda x: x.split('_')[0])
culture_processed['region'] = culture_processed['행정구역'].apply(lambda x: x.split('_')[1])
culture_processed = culture_processed.iloc[:, 1:]
filt_region = list(culture_processed['region'].unique())

parks = parks.loc[parks['region'].isin(filt_region) == True, :]
parks = parks.reset_index(drop=True)

culture_processed = parks.merge(culture_processed,
                                on = 'region',
                                how = 'left')

culture_processed = culture_processed.rename(columns={'num_parks': '공원수'})
culture_processed = culture_processed.drop(columns=['state_y'])
culture_processed['총시설수'] = culture_processed.iloc[:,2:].sum(axis=1).astype('int')

# ===================================
th = datasets['theater'].copy()

fil_state = ['취소/말소/만료/정지/중지', '폐업', '휴업']
th = th.loc[~th['영업상태명'].isin(fil_state), ].reset_index(drop=True)

fil_type = ['자동차극장']
th = th.loc[~th['공연장형태구분명'].isin(fil_type), ].reset_index(drop=True)

th['사업장명'] = th['사업장명'].str.replace(r'\(.*?\)', '', regex=True)
th['사업장명'] = th['사업장명'].str.replace(r'\s*\d+관$', '', regex=True)
th = th.drop_duplicates(['사업장명'], keep='first')

address_col = '소재지전체주소'
th = concat_all(th, 
                address_col, 
                'theater')

th = th.loc[th['region'].isin(filt_region) == True, ]
th = th.rename(columns={'num_theater': '영화관수'})

culture_processed = th.merge(culture_processed,
                            on = 'region',
                            how = 'left')
culture_processed = culture_processed.drop(columns=['state_x','총 시설 수', '총시설수'])
culture_processed['총시설수'] = culture_processed.iloc[:,2:].sum(axis=1).astype('int')

# culture_processed.to_csv('./preprocessed_dataset/8_culture.csv', header=True, index=False)