import os
import urllib.parse
import httpx
import streamlit as st

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/")

def is_oauth_configured() -> bool:
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

def get_google_auth_url() -> str:
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account"
    }
    encoded = urllib.parse.urlencode(params)
    return f"https://accounts.google.com/o/oauth2/auth?{encoded}"

async def exchange_code_for_user_info(code: str) -> dict:
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Exchange auth code for access token
            res = await client.post(token_url, data=data)
            res.raise_for_status()
            tokens = res.json()
            access_token = tokens.get("access_token")
            
            if not access_token:
                return {}
                
            # 2. Query Google UserInfo API
            info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            info_res = await client.get(info_url, headers=headers)
            info_res.raise_for_status()
            profile = info_res.json()
            
            return {
                "google_id": profile.get("sub"),
                "email": profile.get("email"),
                "name": profile.get("name"),
                "picture_url": profile.get("picture")
            }
    except Exception as e:
        print(f"[OAuth Error] Code exchange failed: {e}")
        return {}

def handle_oauth_callback(db_provider) -> dict:
    """Check query params for OAuth redirection code and authenticate user."""
    if not is_oauth_configured():
        return {}
        
    query_params = st.query_params
    if "code" in query_params:
        auth_code = query_params["code"]
        
        # We must resolve the async function in Streamlit sync context
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user_info = loop.run_until_complete(exchange_code_for_user_info(auth_code))
        finally:
            loop.close()
            
        if user_info:
            # Clear authorization code from query params to keep URL clean
            # Workaround: st.query_params.clear() does not instantly clear URL but preserves state
            st.query_params.clear()
            
            # Retrieve or create profile in database
            google_id = user_info["google_id"]
            existing = db_provider.get_user_profile(google_id)
            if not existing:
                user_info["streak_count"] = 1
                user_info["last_active_date"] = None
                user_info["study_pace"] = 15
                db_provider.save_user_profile(user_info)
                return user_info
            else:
                return existing
    return {}
