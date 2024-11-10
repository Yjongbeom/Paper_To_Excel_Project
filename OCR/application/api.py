import requests
import os

api_key = os.getenv('upstage_key')  # 업스테이지 API 키

def ocr_document(filename, folder):
    url = "https://api.upstage.ai/v1/document-ai/ocr"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        with open(filename, "rb") as file:
            response = requests.post(url, headers=headers, files={"document": file})
        response.raise_for_status()
        data = response.json()
        
        return data
    except requests.RequestException as e:
        print(f"Error performing OCR on {os.path.basename(filename)}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {os.path.basename(filename)}: {e}")
        return None
