from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter
from weaviate.classes.config import Property, DataType
from pydantic import BaseModel
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Weaviate client setup
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
)

def ensure_collection_exists():
    """Ensure the UserProfile collection exists and is ready"""
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            if not client.collections.exists("UserProfile"):
                print("Creating UserProfile collection...")
                client.collections.create(
                    name="UserProfile",
                    description="Collection storing user profiles for Muse app",
                    properties=[
                        Property(
                            name="spotifyId",
                            data_type=DataType.TEXT,
                            description="Spotify user ID",
                        ),
                        Property(
                            name="displayName",
                            data_type=DataType.TEXT,
                            description="User's display name from Spotify",
                        ),
                        Property(
                            name="museUsername",
                            data_type=DataType.TEXT,
                            description="User's unique username in Muse",
                        ),
                        Property(
                            name="topArtists",
                            data_type=DataType.TEXT_ARRAY,
                            description="User's top artists from Spotify",
                        ),
                        Property(
                            name="topGenres",
                            data_type=DataType.TEXT_ARRAY,
                            description="User's top genres from Spotify",
                        ),
                        Property(
                            name="recentTracks",
                            data_type=DataType.TEXT_ARRAY,
                            description="User's recently played tracks from Spotify",
                        ),
                        Property(
                            name="friends",
                            data_type=DataType.TEXT_ARRAY,
                            description="List of friend's museUsernames",
                        ),
                    ],
                )
                print("UserProfile collection created successfully")
                
            # Verify the collection exists and is ready
            collection = client.collections.get("UserProfile")
            if collection is None:
                raise Exception("Collection not ready")
                
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to create/verify collection after {max_retries} attempts: {str(e)}")
                raise

# Try to ensure collection exists at startup
try:
    ensure_collection_exists()
except Exception as e:
    print(f"Warning: Failed to create/verify collection at startup: {str(e)}")

class UserProfile(BaseModel):
    spotifyId: str
    displayName: str
    museUsername: str
    topArtists: List[str]
    topGenres: List[str]
    recentTracks: List[str]
    friends: List[str] = []  # List of friend's museUsernames

class UsernameUpdate(BaseModel):
    new_username: str

@router.post("/profile")
async def create_user_profile(profile: UserProfile):
    """Create or update user profile in Weaviate"""
    try:
        ensure_collection_exists()
        
        # Create data object in Weaviate
        data_object = {
            "spotifyId": profile.spotifyId,
            "displayName": profile.displayName,
            "museUsername": profile.museUsername,
            "topArtists": profile.topArtists,
            "topGenres": profile.topGenres,
            "recentTracks": profile.recentTracks,
            "friends": profile.friends
        }
        
        client.collections.get("UserProfile").data.insert(data_object)
        
        return {"message": "Profile created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile")
async def get_user_profile(access_token: str = Header(..., alias="access-token")):
    """Get user profile from Spotify and store in Weaviate"""
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token provided")
        
    try:
        ensure_collection_exists()
        
        # Initialize Spotify client with access token
        sp = spotipy.Spotify(auth=access_token)
        
        try:
            # Test the access token by making a simple API call
            sp.current_user()
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid access token")
        
        # Get user profile
        user = sp.current_user()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user already exists in Weaviate
        user_collection = client.collections.get("UserProfile")
        existing_user = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(user['id'])
        )
        
        if existing_user.objects:
            # User exists, return their profile
            return existing_user.objects[0].properties
        
        # Get top artists
        top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')
        artist_names = [artist['name'] for artist in top_artists['items']]
        
        # Get top genres (from top artists)
        genres = set()
        for artist in top_artists['items']:
            genres.update(artist['genres'])
        top_genres = list(genres)[:5]  # Take top 5 genres
        
        # Get recent tracks
        recent_tracks = sp.current_user_recently_played(limit=5)
        track_names = [item['track']['name'] for item in recent_tracks['items']]
        
        # Create profile data with initial muse_username as Spotify ID
        profile_data = {
            "spotifyId": user['id'],
            "displayName": user['display_name'],
            "museUsername": user['id'],  # Initial username is Spotify ID
            "topArtists": artist_names,
            "topGenres": top_genres,
            "recentTracks": track_names,
            "friends": []
        }
        
        # Store in Weaviate
        user_collection.data.insert(profile_data)
        
        return profile_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/profile/{spotify_id}/username")
async def update_username(spotify_id: str, username_update: UsernameUpdate):
    """Update user's Muse username"""
    try:
        print(f"Received username update request for user {spotify_id}")
        print(f"New username: {username_update.new_username}")
        
        ensure_collection_exists()
        
        if not username_update.new_username:
            print("Error: Empty username provided")
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        # Check if the user exists
        user_collection = client.collections.get("UserProfile")
        print("Fetching user from database...")
        user_result = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(spotify_id)
        )
        
        if not user_result.objects:
            print(f"Error: User {spotify_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"Found user: {user_result.objects[0].properties['displayName']}")
        
        # Get the user's UUID
        user_uuid = user_result.objects[0].uuid
        print(f"User UUID: {user_uuid}")
        
        # Check if username is already taken by a different user
        print("Checking if username is already taken...")
        existing_user = user_collection.query.fetch_objects(
            filters=Filter.by_property("museUsername").equal(username_update.new_username)
        )
        
        if existing_user.objects and existing_user.objects[0].properties["spotifyId"] != spotify_id:
            print(f"Error: Username {username_update.new_username} already taken")
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Update username
        try:
            print("Updating username in database...")
            user_collection.data.update(
                uuid=user_uuid,
                properties={
                    "museUsername": username_update.new_username
                }
            )
            print("Username updated successfully")
        except Exception as e:
            print(f"Error updating username in Weaviate: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update username in database")
        
        return {"message": "Username updated successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Unexpected error in update_username: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compatibility/{user1_id}/{user2_id}")
async def get_compatibility(user1_id: str, user2_id: str):
    """Calculate compatibility between two users"""
    try:
        ensure_collection_exists()
        
        user_collection = client.collections.get("UserProfile")
        
        # Get both user profiles
        user1_result = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(user1_id)
        )
        user2_result = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(user2_id)
        )
        
        if not user1_result.objects or not user2_result.objects:
            raise HTTPException(status_code=404, detail="One or both users not found")
            
        user1 = user1_result.objects[0].properties
        user2 = user2_result.objects[0].properties
        
        # Simple compatibility calculation based on shared artists and genres
        shared_artists = set(user1["topArtists"]) & set(user2["topArtists"])
        shared_genres = set(user1["topGenres"]) & set(user2["topGenres"])
        
        # Calculate compatibility score (0-100)
        artist_score = len(shared_artists) / max(len(user1["topArtists"]), len(user2["topArtists"])) * 50
        genre_score = len(shared_genres) / max(len(user1["topGenres"]), len(user2["topGenres"])) * 50
        
        total_score = artist_score + genre_score
        
        return {
            "compatibility_score": round(total_score, 2),
            "shared_artists": list(shared_artists),
            "shared_genres": list(shared_genres)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/friends/{spotify_id}")
async def get_friends(spotify_id: str, access_token: str = Header(..., alias="access-token")):
    """Get user's friends list"""
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token provided")

    try:
        print(f"Getting friends for user {spotify_id}")
        # Initialize Spotify client with access token to validate it
        sp = spotipy.Spotify(auth=access_token)
        try:
            # Test the access token
            sp.current_user()
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid access token")

        ensure_collection_exists()
        user_collection = client.collections.get("UserProfile")
        
        # Get the user
        user_result = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(spotify_id)
        )
        
        if not user_result.objects:
            print(f"User {spotify_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_result.objects[0]
        print(f"Found user: {user.properties['displayName']} with properties: {user.properties}")
        
        # Ensure we have a list, even if empty
        friends_usernames = user.properties.get("friends", []) or []
        print(f"Friends usernames: {friends_usernames}")
        
        # Get all friends' profiles
        friends = []
        for friend_username in friends_usernames:
            print(f"Looking up friend: {friend_username}")
            friend_result = user_collection.query.fetch_objects(
                filters=Filter.by_property("museUsername").equal(friend_username)
            )
            
            if friend_result.objects:
                friend = friend_result.objects[0]
                print(f"Found friend: {friend.properties['displayName']}")
                friends.append({
                    "displayName": friend.properties["displayName"],
                    "museUsername": friend.properties["museUsername"],
                    "spotifyId": friend.properties["spotifyId"],
                    "profileImageUrl": friend.properties.get("profileImageUrl", "")
                })
            else:
                print(f"Friend {friend_username} not found in database")
        
        print(f"Returning {len(friends)} friends")
        return friends
    except Exception as e:
        print(f"Error in get_friends: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/friends/{spotify_id}/{friend_username}")
async def add_friend(spotify_id: str, friend_username: str):
    ensure_collection_exists()
    user_collection = client.collections.get("UserProfile")
    
    # Get the current user
    user_result = user_collection.query.fetch_objects(
        filters=Filter.by_property("spotifyId").equal(spotify_id)
    )
    
    if not user_result.objects:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the friend
    friend_result = user_collection.query.fetch_objects(
        filters=Filter.by_property("museUsername").equal(friend_username)
    )
    
    if not friend_result.objects:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    user = user_result.objects[0]
    friend = friend_result.objects[0]
    
    # Check if they're already friends
    current_friends = user.properties.get("friends", [])
    if friend.properties["museUsername"] in current_friends:
        raise HTTPException(status_code=400, detail="Already friends with this user")
    
    # Calculate compatibility score
    compatibility_score = calculate_compatibility(
        user.properties["topArtists"],
        user.properties["topGenres"],
        friend.properties["topArtists"],
        friend.properties["topGenres"]
    )
    
    # Add friend to user's friends list
    try:
        user_collection.data.update(
            uuid=user.uuid,
            properties={
                "friends": current_friends + [friend.properties["museUsername"]]
            }
        )
        
        # Add user to friend's friends list (mutual friendship)
        friend_current_friends = friend.properties.get("friends", [])
        user_collection.data.update(
            uuid=friend.uuid,
            properties={
                "friends": friend_current_friends + [user.properties["museUsername"]]
            }
        )
    except Exception as e:
        print(f"Error updating friends: {e}")
        raise HTTPException(status_code=500, detail="Failed to update friends")
    
    return {
        "friend": {
            "displayName": friend.properties["displayName"],
            "museUsername": friend.properties["museUsername"]
        },
        "compatibility_score": compatibility_score
    }

def calculate_compatibility(user_artists: List[str], user_genres: List[str], 
                          friend_artists: List[str], friend_genres: List[str]) -> int:
    # Calculate artist overlap
    common_artists = set(user_artists) & set(friend_artists)
    artist_score = len(common_artists) / max(len(user_artists), 1) * 50
    
    # Calculate genre overlap
    common_genres = set(user_genres) & set(friend_genres)
    genre_score = len(common_genres) / max(len(user_genres), 1) * 50
    
    # Total score is the sum of both scores
    return round(artist_score + genre_score)

@router.get("/search")
async def search_users(username: str):
    try:
        user_collection = client.collections.get("UserProfile")
        
        # Search for users with matching username
        result = user_collection.query.fetch_objects(
            filters=Filter.by_property("museUsername").like(f"*{username}*"),
            limit=5
        )
        
        users = []
        for user in result.objects:
            users.append({
                "displayName": user.properties.get("displayName"),
                "museUsername": user.properties.get("museUsername"),
                "spotifyId": user.properties.get("spotifyId"),
                "profileImageUrl": user.properties.get("profileImageUrl")
            })
        
        return users
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to search users")

@router.get("/{spotify_id}/compatibility/{friend_spotify_id}")
async def get_compatibility(spotify_id: str, friend_spotify_id: str):
    try:
        user_collection = client.collections.get("UserProfile")
        
        # Get both users
        user_result = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(spotify_id)
        )
        friend_result = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(friend_spotify_id)
        )
        
        if not user_result.objects or not friend_result.objects:
            raise HTTPException(status_code=404, detail="User or friend not found")
        
        user = user_result.objects[0]
        friend = friend_result.objects[0]
        
        # Get top artists and genres for both users
        user_artists = user.properties.get("topArtists", [])
        user_genres = user.properties.get("topGenres", [])
        friend_artists = friend.properties.get("topArtists", [])
        friend_genres = friend.properties.get("topGenres", [])
        
        # Calculate compatibility score
        compatibility_score = calculate_compatibility_score(
            user_artists, user_genres, friend_artists, friend_genres
        )
        
        return {
            "compatibilityScore": compatibility_score,
            "commonArtists": list(set(user_artists) & set(friend_artists)),
            "commonGenres": list(set(user_genres) & set(friend_genres)),
            "user1": {
                "displayName": user.properties.get("displayName"),
                "museUsername": user.properties.get("museUsername")
            },
            "user2": {
                "displayName": friend.properties.get("displayName"),
                "museUsername": friend.properties.get("museUsername")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating compatibility: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate compatibility")

@router.delete("/friends/{spotify_id}/{friend_username}")
async def delete_friend(spotify_id: str, friend_username: str, access_token: str = Header(..., alias="access-token")):
    """Remove a friend from user's friends list"""
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token provided")

    try:
        print(f"Removing friend {friend_username} from user {spotify_id}")
        # Initialize Spotify client with access token to validate it
        sp = spotipy.Spotify(auth=access_token)
        try:
            # Test the access token
            sp.current_user()
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid access token")

        ensure_collection_exists()
        user_collection = client.collections.get("UserProfile")
        
        # Get the user
        user_result = user_collection.query.fetch_objects(
            filters=Filter.by_property("spotifyId").equal(spotify_id)
        )
        
        if not user_result.objects:
            print(f"User {spotify_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_result.objects[0]
        print(f"Found user: {user.properties['displayName']}")
        
        # Get current friends list
        friends = user.properties.get("friends", []) or []
        print(f"Current friends: {friends}")
        
        # Remove friend if exists
        if friend_username in friends:
            friends.remove(friend_username)
            print(f"Removed {friend_username} from friends list")
            
            # Update user's friends list
            user_collection.data.update(
                uuid=user.uuid,
                properties={
                    "friends": friends
                }
            )
            print("Friends list updated successfully")
            return {"message": "Friend removed successfully"}
        else:
            print(f"Friend {friend_username} not found in friends list")
            raise HTTPException(status_code=404, detail="Friend not found in friends list")
            
    except Exception as e:
        print(f"Error in delete_friend: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

def calculate_compatibility_score(user_artists: List[str], user_genres: List[str], 
                               friend_artists: List[str], friend_genres: List[str]) -> float:
    """Calculate compatibility score between two users based on shared artists and genres"""
    # Calculate artist overlap
    common_artists = set(user_artists) & set(friend_artists)
    artist_score = len(common_artists) / max(len(user_artists), 1) * 50
    
    # Calculate genre overlap
    common_genres = set(user_genres) & set(friend_genres)
    genre_score = len(common_genres) / max(len(user_genres), 1) * 50
    
    # Total score is the sum of both scores
    return round(artist_score + genre_score, 2) 