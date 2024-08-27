import tabula
import pandas as pd
import numpy as np
import pdfplumber
import re 

path = 'khan_qr.pdf'

# with pdfplumber.open(path) as pdf:
#     num_pages = len(pdf.pages)

# # Read PDF and get list of DataFrames
# area = [160, 0, 810, 900]
# dfs = tabula.read_pdf(path, pages='1', area=area, stream=True, pandas_options={'header': None})

# if num_pages > 1: 
#     other_dfs = []
#     for i in range(2, num_pages + 1):
#         field = [0, 0, 810, 900]
#         df = tabula.read_pdf(path, pages=f'{i}', area=field, stream=True, pandas_options={'header': None})
#         other_dfs.extend(df)
#         print(other_dfs)

# # Concatenate all DataFrames
#     final_df = pd.concat(dfs + other_dfs, axis=0, ignore_index=True)
# else: 
#     final_df = pd.concat(dfs, axis=0, ignore_index=True)

# # Drop the last 11 rows using index
# final_df = final_df.drop(final_df.index[-13:])



# final_df = final_df.rename(columns={
#         0: 'NO',
#         1: 'TRANSACTION_DATE',
#         2: 'BRANCH',
#         3: 'JOURNAL',
#         4: 'CONTACT',
#         5: 'TIME',
#         6: 'DETAILS OF PAYMENT',
#         7: 'CREDIT',
#         8: 'DEBIT',
#         9: 'BALANCE',
#         10: 'ACTUAL_DATE'
#         })
# mask = final_df['NO'].notna() & final_df['NO'].str.contains(' ')

# # Split the 'NO' column values into two parts where necessary
# split_values = final_df.loc[mask, 'NO'].str.split(' ', n=1, expand=True)

# # Assign the split values back to the original DataFrame
# final_df.loc[mask, 'NO'] = split_values[0]
# final_df.loc[mask, 'TRANSACTION_DATE'] = split_values[1]


# # print(final_df)

# final_df['group'] = final_df['NO'].notna().cumsum()
    
#     # Aggregate data by the grouping column
# df_combined = final_df.groupby('group').agg({
#     'NO': 'first',
#     'TRANSACTION_DATE': 'first',
#     'BRANCH': 'first',
#     'JOURNAL': 'first',
#     'CONTACT': 'first',
#     'TIME': 'first',
#     'DETAILS OF PAYMENT': lambda x: ' '.join(str(val) for val in x.dropna()),
#     'CREDIT': 'first',
#     'DEBIT': 'first',
#     'BALANCE': 'first',
#     'ACTUAL_DATE': 'first'
# }).reset_index(drop=True)
    
# print(df_combined)



    # Print the extracted text
    # print(text)

def properties(path):
    with pdfplumber.open(path) as pdf:
        # Select the page (0 for the first page)
        page = pdf.pages[0]

        # Define the area to extract (left, top, right, bottom)
        area = (0, 0, 200, 130)  # Adjust these values based on your needs

        # Extract text from the defined area
        text = page.within_bbox(area).extract_text()

    # Define patterns for different fields
    patterns = {
        'Харилцагчийн нэр': r'Харилцагчийн нэр: ([^\n]+)',
        'Хамтран эзэмшигч': r'Хамтран эзэмшигч: ([^\n]*)',
        'Дансны төрөл': r'Дансны төрөл: ([^\n]+)',
        'Дансны дугаар': r'Дансны дугаар: (\d+)',
        'IBAN no': r'IBAN no: ([A-Z0-9]+)',
        'Валютын төрөл': r'Валютын төрөл: ([A-Z]+)',
    }
    
    # Initialize an empty dictionary to store extracted data
    extracted_data = {}

    # Iterate through the patterns and extract data
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            extracted_data[key] = match.group(1)
    
    return extracted_data


print(properties(path))
