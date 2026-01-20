import os

class Config:
    SECRET_KEY = 'secret_key_for_session_management'
    
    # 1. Get the path to the PROJECT ROOT (Go up one level from 'module_1_ui')
    # os.getcwd() gets the current working directory, but this is safer:
    MODULE_DIR = os.path.dirname(os.path.abspath(__file__)) # .../module_1_ui
    PROJECT_ROOT = os.path.abspath(os.path.join(MODULE_DIR, '..')) # .../EthicX_HR_Project
    
    # 2. Define Shared Database Path
    SHARED_DB_FOLDER = os.path.join(PROJECT_ROOT, 'shared_data')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SHARED_DB_FOLDER, 'ethicx.db')
    
    # 3. Uploads stay inside Module 1 (usually fine, or move to shared if needed)
    UPLOAD_FOLDER = os.path.join(MODULE_DIR, 'uploads')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False