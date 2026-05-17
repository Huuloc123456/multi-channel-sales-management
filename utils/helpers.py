import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_absolute_path(*paths) -> str:
    return os.path.abspath(os.path.join(BASE_DIR, *paths))
