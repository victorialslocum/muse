from fastapi import APIRouter, HTTPException
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from typing import List, Dict
from collections import Counter

router = APIRouter()

# Spotify client setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri="http://localhost:8000/api/auth/callback",
    scope="user-read-private user-read-email user-top-read user-read-recently-played"
))

@router.get("/top-artists/{access_token}")
async def get_top_artists(access_token: str):
    """Get user's top artists"""
    try:
        sp.set_auth(access_token)
        results = sp.current_user_top_artists(limit=20, time_range="medium_term")
        return [{"name": artist["name"], "id": artist["id"]} for artist in results["items"]]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/top-genres/{access_token}")
async def get_top_genres(access_token: str):
    """Get user's top genres"""
    try:
        sp.set_auth(access_token)
        results = sp.current_user_top_artists(limit=50, time_range="medium_term")
        genres = []
        for artist in results["items"]:
            genres.extend(artist["genres"])
        
        # Count and sort genres
        genre_counts = Counter(genres)
        return [{"genre": genre, "count": count} for genre, count in genre_counts.most_common(10)]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/recent-tracks/{access_token}")
async def get_recent_tracks(access_token: str):
    """Get user's recently played tracks"""
    try:
        sp.set_auth(access_token)
        results = sp.current_user_recently_played(limit=20)
        return [{
            "name": item["track"]["name"],
            "artist": item["track"]["artists"][0]["name"],
            "id": item["track"]["id"]
        } for item in results["items"]]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/vibe-analysis/{access_token}")
async def get_vibe_analysis(access_token: str):
    """Get a summary of the user's music taste"""
    try:
        sp.set_auth(access_token)
        
        # Get top artists and genres
        top_artists = await get_top_artists(access_token)
        top_genres = await get_top_genres(access_token)
        recent_tracks = await get_recent_tracks(access_token)
        
        # Analyze the data to create a "vibe" description
        primary_genres = [genre["genre"] for genre in top_genres[:3]]
        vibe_description = f"Your music taste leans towards {', '.join(primary_genres)}. "
        
        # Add some personality based on the genres
        if any(genre in ["indie", "alternative"] for genre in primary_genres):
            vibe_description += "You have an eclectic and independent spirit."
        elif any(genre in ["pop", "dance"] for genre in primary_genres):
            vibe_description += "You're energetic and love to keep the party going."
        elif any(genre in ["rock", "metal"] for genre in primary_genres):
            vibe_description += "You have a strong and passionate personality."
        else:
            vibe_description += "You have a unique and diverse taste in music."
        
        return {
            "vibe_description": vibe_description,
            "top_artists": top_artists[:5],
            "top_genres": top_genres[:5],
            "recent_tracks": recent_tracks[:5]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 