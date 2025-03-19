'use client';

import { useEffect, useState } from 'react';
import { useUser } from '../contexts/UserContext';
import { useRouter, useSearchParams } from 'next/navigation';
import Navigation from '../components/Navigation';

interface SpotifyData {
  recentTracks: string[];
  topArtists: string[];
  topGenres: string[];
}

export default function Dashboard() {
  const { profile, login, updateUsername: contextUpdateUsername } = useUser();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [spotifyData, setSpotifyData] = useState<SpotifyData | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const [newUsername, setNewUsername] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    const urlAccessToken = searchParams.get('access_token');
    if (urlAccessToken) {
      // Store token and login
      login(urlAccessToken).then(() => {
        // Remove access_token from URL by redirecting to clean URL
        router.replace('/dashboard');
      }).catch((error) => {
        console.error('Error logging in:', error);
      });
    }
  }, [searchParams, login, router]);

  // Load Spotify data
  useEffect(() => {
    const loadSpotifyData = async () => {
      if (!profile) return;

      try {
        setSpotifyData({
          recentTracks: profile.recentTracks || [],
          topArtists: profile.topArtists || [],
          topGenres: profile.topGenres || []
        });
      } catch (error) {
        console.error('Error loading Spotify data:', error);
        setError('Failed to load your Spotify data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadSpotifyData();
  }, [profile]);

  const handleUpdateUsername = async () => {
    if (!profile || !newUsername.trim()) {
      return;
    }

    setIsUpdating(true);
    setError(null);

    try {
      await contextUpdateUsername(newUsername);
      setNewUsername('');
    } catch (error) {
      console.error('Error updating username:', error);
      setError(error instanceof Error ? error.message : 'Failed to update username. Please try again later.');
    } finally {
      setIsUpdating(false);
    }
  };

  if (!profile) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-purple-900 to-black text-white">
        <Navigation />
        <div className="max-w-4xl mx-auto p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p>Connecting to Spotify...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-purple-900 to-black text-white">
      <Navigation />
      
      <div className="max-w-4xl mx-auto p-8">
        <div className="bg-white/10 rounded-lg p-6 mb-8">
          <h1 className="text-3xl font-bold mb-2">Welcome, {profile.displayName}!</h1>
          <p className="text-gray-400">@{profile.museUsername}</p>
        </div>

        <div className="space-y-8">
          {/* Username Update Section */}
          <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
            <h2 className="text-xl font-semibold mb-4">Update Username</h2>
            <div className="flex gap-4">
              <input
                type="text"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                placeholder="Enter new username"
                className="flex-1 bg-white/10 rounded-lg px-4 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
              <button
                onClick={handleUpdateUsername}
                disabled={isUpdating}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUpdating ? 'Updating...' : 'Update Username'}
              </button>
            </div>
            {error && (
              <p className="mt-2 text-red-400 text-sm">{error}</p>
            )}
          </div>

          {isLoading ? (
            <div className="text-center py-8">
              <p>Loading your Spotify data...</p>
            </div>
          ) : error ? (
            <div className="text-red-400 text-center py-8">
              <p>{error}</p>
            </div>
          ) : spotifyData && (
            <div className="grid gap-8">
              <section className="bg-white/10 rounded-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Recent Tracks</h2>
                <ul className="space-y-2">
                  {spotifyData.recentTracks.map((track, index) => (
                    <li key={index} className="text-gray-300">{track}</li>
                  ))}
                </ul>
              </section>

              <section className="bg-white/10 rounded-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Top Artists</h2>
                <ul className="space-y-2">
                  {spotifyData.topArtists.map((artist, index) => (
                    <li key={index} className="text-gray-300">{artist}</li>
                  ))}
                </ul>
              </section>

              <section className="bg-white/10 rounded-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Top Genres</h2>
                <ul className="space-y-2">
                  {spotifyData.topGenres.map((genre, index) => (
                    <li key={index} className="text-gray-300">{genre}</li>
                  ))}
                </ul>
              </section>
            </div>
          )}
        </div>
      </div>
    </main>
  );
} 