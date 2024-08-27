import tabula
import pandas as pd
import camelot
import pdfplumber
import re 
 
path = 'huulga.pdf'

#page1----------------------------------------------
df = tabula.read_pdf(path, pages=1)
if not df:
    print("No DataFrame was read from the PDF.")
    exit()

dif = df[0]

dif = dif.dropna(how='all')

first_row = dif.iloc[0]
new_columns = [f"{col} {val}".strip() for col, val in zip(dif.columns, first_row)]
dif.columns = [col.replace('nan', '').strip() for col in new_columns]

dif = dif.iloc[1:].reset_index(drop=True)

dif = dif.fillna('')
# print(dif)

#pages-------------------------------------------------------------------------------------------------
combined_df = None
num_pages = len(tabula.read_pdf(path, pages='all'))

def split_column(value):
        if pd.isna(value) or '\n' not in value:
            return None, value
        before_newline, after_newline = value.split('\n', 1)
        return before_newline.strip(), after_newline.strip()

if num_pages >= 2:
    for i in range(2, num_pages + 1):
        tables = camelot.read_pdf(path, pages=f'{i}', flavor='stream')
        
        if tables:
            # Combine all tables into one DataFrame
            page_df = pd.concat([table.df for table in tables], ignore_index=True)
            
            if combined_df is None:
                combined_df = page_df
            else:
                combined_df = pd.concat([combined_df, page_df], ignore_index=True)

    if combined_df is not None:
        # Apply splitting function to the 5th column (index 5)
        combined_df[['5', '7']] = combined_df[5].apply(split_column).apply(pd.Series)

        # Replace old column 5 with new values
        combined_df[5] = combined_df['5']

        # Drop the old column 5 and rename the new column
        combined_df = combined_df.drop(columns=['5'])
        
        # Swap columns 6 and 7
        temp = combined_df[6].copy()
        combined_df[6] = combined_df['7']
        combined_df[7] = temp
        
        # Drop the old column 7 and fill NaNs
        combined_df = combined_df.drop(columns=['7'])
        combined_df = combined_df.fillna('')

        # Rename columns
        combined_df = combined_df.rename(columns={0: 'Огноо', 1: 'Теллер', 2: 'Орлого', 3: 'Зарлага', 4: 'Ханш', 5: 'Харьцсан данс', 6: 'Үлдэгдэл', 7: 'Гүйлгээний утга'})

        # Concatenate the DataFrames
        dis = pd.concat([dif, combined_df], axis=0, ignore_index=True)
# -------------------------------------------------------------------------------------------------------------------------------------------------------------
else: 
    dis = pd.concat([dif], axis=0, ignore_index=True)
# print(dis.head(20))

group_column = dis.columns[6]  # Assuming the 7th column is at index 6

dis['Group'] = (dis[group_column] != dis[group_column].shift()).cumsum()

last_row = dis.iloc[[-1]]
remaining_data = dis.iloc[:-1]

def merge_group(group):
    return pd.Series({
        'Огноо': ' '.join(str(x) for x in group['Огноо']),
        'Теллер': ' '.join(str(x) for x in group['Теллер']),
        'Орлого': ' '.join(str(x) for x in group['Орлого']),
        'Зарлага': ' '.join(str(x) for x in group['Зарлага']),
        'Ханш': ' '.join(str(x) for x in group['Ханш']),
        'Харьцсан данс': ' '.join(str(x) for x in group['Харьцсан данс']),
        'Үлдэгдэл': group['Үлдэгдэл'].iloc[0],  # Use the first balance in the group
        'Гүйлгээний утга': ' '.join(str(x) for x in group['Гүйлгээний утга'])
    })

grouped = remaining_data.groupby('Group', group_keys=False).apply(merge_group, include_groups=False).reset_index(drop=True)

def custom_merge(series):
    return ' '.join(series)

def merge_rows(data, merge_func):
    # Ensure the length of the DataFrame is even
    if len(data) % 2 != 0:
        # Add the last row if the length is odd
        last_row = data.iloc[[-1]]
        data = pd.concat([data, last_row], ignore_index=True)
        
    # Group every 2 rows and apply merge_func
    return pd.DataFrame({
        col: [merge_func(data[col].iloc[i:i+2]) for i in range(0, len(data), 2)]
        for col in data.columns
    })

data = merge_rows(grouped, custom_merge)

result_df = pd.concat([data, last_row], ignore_index=True)

if 'Group' in result_df.columns:
    result_df = result_df.drop(columns=['Group'])

print(result_df)

with pdfplumber.open(path) as pdf:
    # Select the page (0 for the first page)
    page = pdf.pages[0]

    # Define the area to extract (left, top, right, bottom)
    area = (0, 50, 592, 150)  # Adjust these values based on your needs

    # Extract text from the defined area
    text = page.within_bbox(area).extract_text()

    # Print the extracted text
    

def properties(input):
    patterns = {
    'Хэвлэсэн огноо': r'Хэвлэсэн огноо: (\d{4}\.\d{2}\.\d{2})',
    'Харилцагч': r'Харилцагч: (.*?) \(\d+\)',
    'Дансны дугаар': r'Дансны дугаар: (\d+)',
    'Эхний үлдэгдэл': r'Эхний үлдэгдэл: ([\d,\.]+)',
    'Эцсийн үлдэгдэл': r'Эцсийн үлдэгдэл: ([\d,\.]+)',
    'Боломжит үлдэгдэл': r'Боломжит үлдэгдэл: ([\d,\.]+)',
    'Хамрах хугацаа': r'Хамрах хугацаа: (\d{4}\.\d{2}\.\d{2}[-–]\s*\d{4}\.\d{2}\.\d{2})'
    }
    extracted_data = {key: re.search(pattern, input).group(1) if re.search(pattern, input) else None for key, pattern in patterns.items()}
    return extracted_data

print(properties(text))