import os
import json
from utils import calculate_file_hash

def manage_cache(file_hash, file_path, cache_folder, ocr_function, folder):
    """파일 해시와 캐시 폴더를 관리하며 캐시 파일이 존재하는지 확인합니다."""
    cache_file = os.path.join(cache_folder, f"{file_hash}.json")
    
    if os.path.exists(cache_file):
        print(f"Cache file found for {os.path.basename(file_path)}.")
        return cache_file
    else:
        print(f"Cache file not found for {os.path.basename(file_path)}.")
        return None
