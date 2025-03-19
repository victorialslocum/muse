import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Weaviate client setup
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
)

# Test users data
test_users = [
    {
        # Similar user 1 - Lots of overlap in artists and genres
        "spotifyId": "alex_music_lover",
        "displayName": "Alex",
        "museUsername": "alex_classical",
        "topArtists": [
            "Fred again..",
            "Ludovico Einaudi",
            "SYML",
            "Max Richter",
            "Nils Frahm"
        ],
        "topGenres": [
            "stutter house",
            "house",
            "classical",
            "neoclassical",
            "ambient"
        ],
        "recentTracks": [
            "Less Alone",
            "Experience",
            "Where's My Love",
            "On The Nature of Daylight",
            "Says"
        ],
        "friends": []
    },
    {
        # Similar user 2 - Some overlap
        "spotifyId": "sarah_beats",
        "displayName": "Sarah",
        "museUsername": "sarah_house",
        "topArtists": [
            "Fred again..",
            "Bonobo",
            "Four Tet",
            "Jamie xx",
            "Bicep"
        ],
        "topGenres": [
            "stutter house",
            "house",
            "electronic",
            "techno",
            "ambient"
        ],
        "recentTracks": [
            "Marea (We've Lost Dancing)",
            "Kerala",
            "Only Human",
            "Gosh",
            "Atlas"
        ],
        "friends": []
    },
    {
        # Different user 1 - Metal/Rock
        "spotifyId": "metal_mike",
        "displayName": "Mike",
        "museUsername": "metalhead_mike",
        "topArtists": [
            "Metallica",
            "Iron Maiden",
            "Slayer",
            "Megadeth",
            "Black Sabbath"
        ],
        "topGenres": [
            "metal",
            "heavy metal",
            "thrash metal",
            "rock",
            "classic rock"
        ],
        "recentTracks": [
            "Master of Puppets",
            "The Trooper",
            "Angel of Death",
            "Holy Wars",
            "Paranoid"
        ],
        "friends": []
    },
    {
        # Different user 2 - Country
        "spotifyId": "country_carol",
        "displayName": "Carol",
        "museUsername": "country_carol",
        "topArtists": [
            "Luke Combs",
            "Morgan Wallen",
            "Chris Stapleton",
            "Luke Bryan",
            "Blake Shelton"
        ],
        "topGenres": [
            "country",
            "contemporary country",
            "country road",
            "country pop",
            "modern country rock"
        ],
        "recentTracks": [
            "Beautiful Crazy",
            "Whiskey Glasses",
            "Tennessee Whiskey",
            "Country Girl",
            "God's Country"
        ],
        "friends": []
    }
]

def add_test_users():
    user_collection = client.collections.get("UserProfile")
    
    for user in test_users:
        try:
            # Check if user already exists
            existing = user_collection.query.fetch_objects(
                filters=weaviate.classes.query.Filter.by_property("spotifyId").equal(user["spotifyId"])
            )
            
            if not existing.objects:
                user_collection.data.insert(user)
                print(f"Added user: {user['displayName']} (@{user['museUsername']})")
            else:
                print(f"User already exists: {user['displayName']} (@{user['museUsername']})")
                
        except Exception as e:
            print(f"Error adding user {user['displayName']}: {str(e)}")

if __name__ == "__main__":
    add_test_users()
    print("\nTest users you can add as friends:")
    print("1. @alex_classical (similar music taste)")
    print("2. @sarah_house (similar music taste)")
    print("3. @metalhead_mike (different music taste)")
    print("4. @country_carol (different music taste)") 