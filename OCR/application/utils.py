import hashlib
import re

def calculate_file_hash(filepath):
    """파일의 해시값을 계산합니다."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        print(f"Error calculating hash for {filepath}: {e}")
    return hash_md5.hexdigest()

def normalize_column_name(name):
    """열 제목을 정규화합니다."""
    return re.sub(r'\W+', ' ', name).strip().lower()
