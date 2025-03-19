import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Weaviate client setup
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
)

def delete_user(spotify_id: str):
    user_collection = client.collections.get("UserProfile")
    
    # Get the user
    user_result = user_collection.query.fetch_objects(
        filters=Filter.by_property("spotifyId").equal(spotify_id)
    )
    
    if not user_result.objects:
        print(f"User with Spotify ID {spotify_id} not found")
        return
    
    user = user_result.objects[0]
    print(f"Found user: {user.properties['displayName']} (@{user.properties['museUsername']})")
    
    try:
        # Delete the user using the UUID
        user_collection.data.delete_by_id(user.uuid)
        print(f"Successfully deleted user with Spotify ID {spotify_id}")
    except Exception as e:
        print(f"Error deleting user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    spotify_id = "victoriaslo235"  # Your Spotify ID
    delete_user(spotify_id)
    print("\nYou can now log in again to recreate your profile with the correct schema.") 