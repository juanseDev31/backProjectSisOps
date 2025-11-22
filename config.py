import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu-secret-key-cambiar-en-produccion')
    SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://hhpjfofxafntdpewblkz.supabase.co')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_secret_5u1LfH5JUUfH11n8Cd45bw_hGgRbLWZ')