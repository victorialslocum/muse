# Muse - Music Compatibility App

Muse is a web application that connects users based on their music taste. The app analyzes your Spotify listening history to determine your musical "vibe" and helps you find compatible music lovers.

## Project Structure

```
muse/
├── backend/         # FastAPI backend
│   ├── app/        # Main application code
│   ├── tests/      # Backend tests
│   └── requirements.txt
└── frontend/       # Next.js frontend
    ├── src/        # Source code
    ├── public/     # Static files
    └── package.json
```

## Features (MVP)

- Spotify OAuth authentication
- User music taste analysis
- Basic user profile
- User compatibility matching

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Spotify API credentials and Weaviate configuration
```

4. Run the backend:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your backend API URL and Spotify client ID
```

3. Run the development server:
```bash
npm run dev
```

## Environment Variables

### Backend (.env)
- `SPOTIFY_CLIENT_ID`: Your Spotify API client ID
- `SPOTIFY_CLIENT_SECRET`: Your Spotify API client secret
- `WEAVIATE_URL`: Your Weaviate instance URL
- `WEAVIATE_API_KEY`: Your Weaviate API key

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_SPOTIFY_CLIENT_ID`: Your Spotify API client ID 