import os

from dotenv import load_dotenv


# 加载项目根目录 .env 中的环境变量。
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEEPSEEK_MODEL = "deepseek-v4-flash"
BASE_URL = "https://api.deepseek.com"
