#!/bin/bash

echo "Welcome to Muse Setup! 🎵"
echo "This script will help you set up your environment variables for both backend and frontend."

# Backend setup
echo -e "\n=== Backend Setup ==="
echo "Please enter your Spotify API credentials:"
read -p "Spotify Client ID: " spotify_client_id
read -p "Spotify Client Secret: " spotify_client_secret

echo -e "\nPlease enter your Weaviate configuration:"
read -p "Weaviate URL: " weaviate_url
read -p "Weaviate API Key: " weaviate_api_key
read -p "OpenAI API Key: " openai_api_key

# Create backend .env file
cat > backend/.env << EOL
SPOTIFY_CLIENT_ID=$spotify_client_id
SPOTIFY_CLIENT_SECRET=$spotify_client_secret
WEAVIATE_URL=$weaviate_url
WEAVIATE_API_KEY=$weaviate_api_key
OPENAI_API_KEY=$openai_api_key
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOL

# Frontend setup
echo -e "\n=== Frontend Setup ==="
echo "Please enter your frontend configuration:"
read -p "Backend API URL (default: http://localhost:8000): " backend_url
backend_url=${backend_url:-http://localhost:8000}

# Create frontend .env.local file
cat > frontend/.env.local << EOL
NEXT_PUBLIC_API_URL=$backend_url
NEXT_PUBLIC_SPOTIFY_CLIENT_ID=$spotify_client_id
NEXT_PUBLIC_SPOTIFY_REDIRECT_URI=http://localhost:3000/api/auth/callback
EOL

echo -e "\n✅ Setup complete! Your environment variables have been configured."
echo -e "\nNext steps:"
echo "1. Start the backend server:"
echo "   cd backend"
echo "   python -m venv venv"
echo "   source venv/bin/activate  # On Windows: .\\venv\\Scripts\\activate"
echo "   pip install -r requirements.txt"
echo "   uvicorn app.main:app --reload"
echo -e "\n2. Start the frontend development server:"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo -e "\n3. Visit http://localhost:3000 in your browser" 