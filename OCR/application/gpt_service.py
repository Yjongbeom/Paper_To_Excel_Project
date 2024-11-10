# import openai
# import hashlib
# import json
# import io
# import pandas as pd
# import re
# import os

# # OpenAI API 키 설정
# openai.api_key = os.getenv('openai_key')

# def get_gpt_columns(text):
#     """GPT에게 파일 내용을 보내어 열 제목을 추출합니다."""
#     text_hash = hashlib.md5(text.encode()).hexdigest()
#     gpt_cache_file = os.path.join('gpt_cache', f"{text_hash}.json")
    
#     if os.path.exists(gpt_cache_file):
#         print("GPT response found in cache.")
#         try:
#             with open(gpt_cache_file, "r") as f:
#                 response = json.load(f)
#                 column_names = response['column_names']
#                 return [col.strip() for col in column_names.split(',')]
#         except Exception as e:
#             print(f"Error reading GPT cache file {gpt_cache_file}: {e}")
#             return []
#     else:
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "system", "content": (
#                         "You are a skilled data analyst. Extract and return the most relevant column names from the provided text. "
#                         "Ensure that the column names are concise, relevant, and free of typographical errors. "
#                         "The column names should be in Korean and should match the data context exactly."
#                     )},
#                     {"role": "user", "content": f"{text}"}
#                 ]
#             )
#             column_names = response['choices'][0]['message']['content']
#             with open(gpt_cache_file, "w") as f:
#                 json.dump({'column_names': column_names}, f)
#             columns = [col.strip() for col in column_names.split(',')]
#             return columns
#         except Exception as e:
#             print(f"Error getting columns from GPT: {e}")
#             return []

# def extract_table_from_text(text, columns):
#     """GPT를 사용하여 텍스트에서 표 형식으로 변환된 데이터를 DataFrame으로 변환합니다."""
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": (
#                     "You are an AI that extracts structured information from text. "
#                     "Extract the data into a table format with the following columns. "
#                     "Ensure to include all columns and rows. If any data is missing, use '-' to indicate it. "
#                     "Make sure that bank account details, such as 'Account Number' and 'Bank Name', are separated correctly. "
#                     "If there's a classification and date, please put it in"
#                     "Do not merge these columns and ensure consistency across all rows. "
#                     "Use '-' if any column value is missing or not available."
#                 )},
#                 {"role": "user", "content": (
#                     "Here is the text with information that needs to be converted into a table. "
#                     "The table should have the following columns: " + ', '.join(columns) + ".\n\n" + text
#                 )}
#             ]
#         )
        
#         table_markdown = response['choices'][0]['message']['content']
#         print(f"Extracted Table Markdown:\n{table_markdown}")

#         if '| Field | Value |' in table_markdown:
#             rows = table_markdown.splitlines()[2:]
#             data = {}
#             for row in rows:
#                 if '|' in row:
#                     key, value = [col.strip() for col in row.split('|')[1:-1]]
#                     data[key] = value
#             df = pd.DataFrame([data])
#             return df

#         else:
#             # Markdown 테이블을 DataFrame으로 변환
#             try:
#                 table_io = io.StringIO(table_markdown)
#                 table_lines = table_io.readlines()

#                 if len(table_lines) < 3:
#                     print("Insufficient table data.")
#                     return pd.DataFrame()

#                 headers = table_lines[0].strip().split('|')[1:-1]
#                 headers = [header.strip() for header in headers]

#                 data = [line.strip().split('|')[1:-1] for line in table_lines[2:]]

#                 df = pd.DataFrame(data, columns=headers)

#                 return df

#             except Exception as e:
#                 print(f"Error reading table markdown into DataFrame: {e}")
#                 return pd.DataFrame()

#     except Exception as e:
#         print(f"Error extracting table from text: {e}")
#         return pd.DataFrame()

import hashlib
import json
import io
import pandas as pd
import re
import requests
import os

AI_COLUMNS_ENDPOINT = os.getenv('AI_COLUMNS_ENDPOINT')
AI_RESPONSE_ENDPOINT = os.getenv('AI_RESPONSE_ENDPOINT')

def get_ai_columns(text):
    """AI 서버에 파일 내용을 보내어 열 제목을 추출합니다."""
    text_hash = hashlib.md5(text.encode()).hexdigest()
    gpt_cache_file = os.path.join('gpt_cache', f"{text_hash}.json")
    
    if os.path.exists(gpt_cache_file):
        print("AI response found in cache.")
        try:
            with open(gpt_cache_file, "r") as f:
                response = json.load(f)
                column_names = response['column_names']
                return [col.strip() for col in column_names.split(',')]
        except Exception as e:
            print(f"Error reading GPT cache file {gpt_cache_file}: {e}")
            return []
    else:
        try:
            response = requests.post(AI_COLUMNS_ENDPOINT, json={"text": text})

            if response.status_code == 200:
                response_data = response.json()
                column_names = response_data['response']

                if column_names:
                    columns = [col.strip() for col in column_names.split(',')]
                    with open(gpt_cache_file, "w") as f:
                        json.dump({'column_names': column_names}, f)
                    return columns
                else:
                    print("Error: No column names found in AI response.")
                    return []
            else:
                print(f"Error from AI API: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"Error getting columns from AI: {e}")
            return []

def clean_and_format_table(table_markdown):
    """AI 서버에서 받은 데이터를 정리하여 DataFrame으로 변환"""
    try:
        table_io = io.StringIO(table_markdown)
        table_lines = table_io.readlines()

        if len(table_lines) < 3:
            print("Insufficient table data.")
            return pd.DataFrame()

        # 첫 번째 줄에서 열 이름을 추출
        headers = table_lines[0].strip().split('|')[1:-1]
        headers = [header.strip() for header in headers]

        # 데이터 행을 처리
        data = []
        for line in table_lines[2:]:
            row_data = line.strip().split('|')[1:-1]
            row_data = [cell.strip() for cell in row_data]

            if not row_data or all(cell == '' for cell in row_data):
                continue

            # 데이터의 길이가 열의 길이와 다르면 처리
            if len(row_data) < len(headers):
                # 데이터가 부족한 경우 NaN으로 채움
                row_data.extend([None] * (len(headers) - len(row_data)))
            elif len(row_data) > len(headers):
                # 데이터가 초과한 경우, 여분의 데이터를 무시하거나 별도로 처리
                row_data = row_data[:len(headers)]  # 일단 추가 데이터를 무시

            data.append(row_data)

        # DataFrame으로 변환
        df = pd.DataFrame(data, columns=headers)
        return df

    except Exception as e:
        print(f"Error cleaning and formatting table: {e}")
        return pd.DataFrame()

def extract_table_from_text(text, columns):
    """AI 서버에 텍스트에서 표 형식으로 변환된 데이터를 DataFrame으로 변환합니다."""
    try:
        response = requests.post(AI_RESPONSE_ENDPOINT, json={
            "text": text,
            "columns": columns
        })

        if response.status_code == 200:
            response_data = response.json()
            table_markdown = response_data['response']
            print(f"Extracted Table Markdown:\n{table_markdown}")

            # 표 형식의 데이터를 DataFrame으로 변환
            df = clean_and_format_table(table_markdown)
            return df

        else:
            print(f"Error from AI API: {response.status_code}, {response.text}")
            return pd.DataFrame()

    except Exception as e:
        print(f"Error extracting table from text: {e}")
        return pd.DataFrame()

