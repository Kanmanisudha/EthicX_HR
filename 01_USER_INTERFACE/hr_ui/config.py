import os

class Config:
    """
    Nature: Centralized Configuration for the EthicX-HR Ecosystem.
    This file defines where data lives and how microservices find each other.
    """
    
    # Security key for Flask-Login session encryption
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ethicx-secret-key-2026-ignite'

    # --- 1. PATH CALCULATIONS ---
    # MODULE_DIR: Points to the current folder (01_USER_INTERFACE)
    # PROJECT_ROOT: Points to the main project folder
    MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(MODULE_DIR, '..'))

    # --- 2. SHARED DATABASE ---
    # We place the DB in a shared folder so multiple tiers can potentially access it
    SHARED_DB_FOLDER = os.path.join(PROJECT_ROOT, 'shared_data')
    
    # Ensure the shared folder exists before initializing the DB path
    if not os.path.exists(SHARED_DB_FOLDER):
        os.makedirs(SHARED_DB_FOLDER)
        print(f"📁 Created Shared Data Folder at: {SHARED_DB_FOLDER}")

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SHARED_DB_FOLDER, 'ethicx.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- 3. UPLOADS MANAGEMENT ---
    # Resumes are stored here for parsing by Module 04A (Applicant Service)
    UPLOAD_FOLDER = os.path.join(MODULE_DIR, 'uploads')
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"📁 Created Uploads Folder at: {UPLOAD_FOLDER}")

    # --- 4. MICROSERVICE ENDPOINTS ---
    # Defines the entry point for the downstream orchestration
    ORCHESTRATOR_URL = "http://127.0.0.1:5001/orchestrate/screening"