import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('FSTR_DB_HOST', 'localhost')
DB_PORT = os.getenv('FSTR_DB_PORT', '5432')
DB_LOGIN = os.getenv('FSTR_DB_LOGIN', 'postgres')
DB_PASS = os.getenv('FSTR_DB_PASS', 'postgres')
DB_NAME = os.getenv('FSTR_DB_NAME', 'fstr_db')

DATABASE_URL = f"postgresql://{DB_LOGIN}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"