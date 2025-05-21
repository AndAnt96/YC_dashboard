import os
import pandas as pd

def load_datasets(category: str) -> pd.DataFrame:
    r_path = f'./data/{category}'
    f_dir = os.listdir(r_path)
    encod_options = ['cp949','euc-kr', 'utf-16', 'ascii']
    
    datasets = dict()
    for f in f_dir:
        f_path = os.path.join(r_path, f'{f}')
        f_name = f.split('.')[0]
        try:
            datasets[f_name] = pd.read_csv(f_path)
        except UnicodeDecodeError:
            i = 0
            while i < len(encod_options):
                try: 
                    datasets[f_name] = pd.read_csv(f_path, encoding=encod_options[i])
                    i = len(encod_options)
                except UnicodeDecodeError:
                    i += 1
                    continue
    return datasets

