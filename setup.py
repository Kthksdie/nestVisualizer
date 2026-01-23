import requests
import json
import urllib.parse
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Your Device Access Project ID (UUID format)
PROJECT_ID = os.getenv("PROJECT_ID")

# Configuration
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

DEVICE_AUTH_URL = f"https://nestservices.google.com/partnerconnections/{PROJECT_ID}/auth"
REDIRECT_URI = "https://www.google.com"
SCOPE = "https://www.googleapis.com/auth/sdm.service"

def main():
    print("--- Google OAuth2 Setup ---")
    
    # 1. Generate Authorization URL
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent" 
    }
    
    auth_url = f"{DEVICE_AUTH_URL}?" + urllib.parse.urlencode(auth_params)
    
    print("\n1. Go to the following URL in your browser:")
    print("   (You may see a warning about the app not being verified - proceed anyway if it's your app)")
    print(f"\n{auth_url}\n")
    
    print("2. Log in with your Google account.")
    print("3. You will be redirected to google.com with a ?code=... in the URL.")
    print("4. Copy the entire 'code' value from the URL (everything after code= and before any other & symbol).")
    
    # 2. Get the authorization code from the user
    auth_code = input("\nEnter the authorization code here: ").strip()
    
    if not auth_code:
        print("No code entered. Exiting.")
        return

    # 3. Exchange code for tokens
    print("\nExchanging code for tokens...")
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        print("\nSUCCESS! Here are your tokens:")
        print("-" * 60)
        print(json.dumps(tokens, indent=2))
        print("-" * 60)
        
        if "refresh_token" in tokens:
            print("\nIMPORTANT: Copy the 'refresh_token' above and update your 'nestDetails.py' file with it.")
            print(f"Current implementation in nestDetails.py expects: REFRESH_TOKEN = \"{tokens['refresh_token']}\"")
        else:
            print("\nWARNING: No refresh_token returned. Did you click 'Allow' on the consent screen?")
            print("Note: Refresh tokens are only returned on the first authorization or if access_type=offline and prompt=consent.")
            
    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Failed to retrieve tokens.")
        print(e)
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    main()