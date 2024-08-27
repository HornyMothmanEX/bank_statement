import camelot
import re
import pandas as pd 
import tabula
import numpy as np
import pdfplumber

path = 'golomt_qr.pdf'
with pdfplumber.open(path) as pdf:
    num_pages = len(pdf.pages)
area = [160, 0, 810, 900]
dfs = tabula.read_pdf(path, pages='1', area=area, stream=True)
dif = dfs[0]

dif = dif.dropna(how='all')

first_row = dif.iloc[0]
new_columns = [f"{col} {val}".strip() for col, val in zip(dif.columns, first_row)]
dif.columns = [col.replace('nan', '').strip() for col in new_columns]

dif = dif.iloc[1:].reset_index(drop=True)
dif = dif.drop('ДҮН /AMOUNT ВАЛЮТ/IN FC', axis=1)
dif = dif.rename(columns={
        'ОГНОО DATE': 'DATE',
        'Unnamed: 0 MNT': 'AMOUNT',
        'ТӨРӨЛ TYPE': 'TYPE',
        'ГҮЙЛГЭЭНИЙ УТГА DETAILS OF PAYMENT': 'DETAILS OF PAYMENT'})


dis = []

def split_row(row):
        if pd.isna(row):
            return pd.Series([None, None, None, None], index=['DATE', 'AMOUNT', 'TYPE', 'DETAILS OF PAYMENT'])
        
        parts = str(row).split(' ')
        
        if len(parts) == 1:
            if parts[0] in ['ОРЛОГО', 'ЗАРЛАГА']:
                return pd.Series([None, None, parts[0], None], index=['DATE', 'AMOUNT', 'TYPE', 'DETAILS OF PAYMENT'])
        
        amount = parts[0]
        payment_type = ' '.join(parts[1:])
        
        # Check if payment_type is 'ОРЛОГО' or 'ЗАРЛАГА'
        if payment_type in ['ОРЛОГО', 'ЗАРЛАГА']:
            return pd.Series([None, amount, payment_type, None], index=['DATE', 'AMOUNT', 'TYPE', 'DETAILS OF PAYMENT'])
        else:
            return pd.Series([None, amount, None, payment_type], index=['DATE', 'AMOUNT', 'TYPE', 'DETAILS OF PAYMENT'])

if num_pages >= 2:
    area2 = [30, 0, 810, 900]
    column_names = ['DATE', 'AMOUNT', 'TYPE', 'DETAILS OF PAYMENT']
    for i in range(2, num_pages + 1):
        dfs = tabula.read_pdf(path, pages=f'{i}', area=area2, stream=True, pandas_options={'header': None})
        if dfs:
            dfs = dfs[0]
            exclude_start_phrase = "Овог, нэр/Full name"
            if dfs[0].str.contains(exclude_start_phrase).any():
                exclude_start_index = dfs[dfs[0].str.contains(exclude_start_phrase, na=False)].index[0]
                dfs = dfs.iloc[:exclude_start_index]
                dfs = dfs[0].apply(split_row)
            else:
                dfs.columns = column_names
            
            dis.append(dfs)
    
    dis = pd.concat(dis, ignore_index=True)
    dif = pd.concat([dif, dis], axis=0, ignore_index=True)
else:
    dif = pd.concat(dif, axis=0, ignore_index=True)

dif['DATE'] = dif['DATE'].ffill()

dif = dif.dropna(subset=['DETAILS OF PAYMENT'], how='all').reset_index(drop=True)



df_copy = dif.copy()


for i in range(1, len(df_copy)):
    if pd.isna(df_copy.loc[i, 'AMOUNT']) and pd.isna(df_copy.loc[i, 'TYPE']):
        df_copy.loc[i-1, 'DETAILS OF PAYMENT'] += " " + str(df_copy.loc[i, 'DETAILS OF PAYMENT'])
        df_copy.loc[i, :] = np.nan

df_copy.dropna(how='all', inplace=True)


df_copy.reset_index(drop=True, inplace=True)
print(df_copy)

