"""Configuration settings for the chatbot and agents"""

# Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyBX5RthSIlT6Ue4u_B03UoHLHHc_BAPpv0"

# SAP HANA Cloud Configuration
# Get these details from your SAP HANA Cloud dashboard
HANA_CONFIG = {
    'host': 'your_hana_host.hana.prod-region.hanacloud.ondemand.com',
    'port': 443,  # Default HANA port
    'user': 'DBADMIN',  # Default admin user
    'password': 'your_password'
}

# Flask Configuration
FLASK_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}

# File Upload Configuration
UPLOAD_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
