# config.py

import os
import pyodbc

class Config:
    DRIVER = '{ODBC Driver 17 for SQL Server}'
    SERVER = os.getenv('DB_SERVER')           # e.g., 'fitnessapp1234.database.windows.net'
    DATABASE = os.getenv('DB_DATABASE')       # e.g., 'firness_app'
    USERNAME = os.getenv('DB_USERNAME')       # e.g., 'fitness_app'
    PASSWORD = os.getenv('DB_PASSWORD')       # e.g., 'task@2025'

    CONNECTION_STRING = (
        f'DRIVER={DRIVER};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'UID={USERNAME};'
        f'PWD={PASSWORD};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=no;'
        f'Connection Timeout=30;'
    )
