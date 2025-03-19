from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from typing import Optional

router = APIRouter()

# Spotify OAuth configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000/api/auth/callback"  # Frontend callback URL

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-read-private user-read-email user-top-read user-read-recently-played"
)

@router.get("/login")
async def login():
    """Get Spotify login URL"""
    auth_url = sp_oauth.get_authorize_url()
    return {"url": auth_url}

@router.get("/callback")
async def callback(code: str):
    """Handle Spotify OAuth callback"""
    try:
        token_info = sp_oauth.get_access_token(code)
        if not token_info:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Return JSON response with access token
        return JSONResponse({
            "access_token": token_info["access_token"],
            "token_type": token_info["token_type"],
            "expires_in": token_info["expires_in"]
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh Spotify access token"""
    try:
        token_info = sp_oauth.refresh_access_token(refresh_token)
        return {"access_token": token_info["access_token"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 