import google.generativeai as genai
from config import GEMINI_API_KEY

def test_gemini_connection():
    try:
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Test with a simple prompt
        response = model.generate_content("Write a short greeting message.")
        
        print("Gemini API Test Results:")
        print("------------------------")
        print("Connection: Success")
        print("Response:", response.text)
        return True
        
    except Exception as e:
        print("Gemini API Test Results:")
        print("------------------------")
        print("Connection: Failed")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    test_gemini_connection()
