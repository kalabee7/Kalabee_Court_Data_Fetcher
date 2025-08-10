import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    COURT_URL = os.environ.get('COURT_URL') or 'https://delhihighcourt.nic.in/'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'court_cases.db'
    
    # Chrome driver settings
    CHROME_OPTIONS = [
        '--headless',  # Run Chrome in background
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1920,1080'
    ]
