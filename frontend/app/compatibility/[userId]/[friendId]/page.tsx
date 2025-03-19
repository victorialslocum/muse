'use client';

import { useEffect, useState } from 'react';
import { useUser } from '../../../contexts/UserContext';
import Navigation from '../../../components/Navigation';
import { useRouter } from 'next/navigation';
import { use } from 'react';

interface CompatibilityData {
  compatibilityScore: number;
  commonArtists: string[];
  commonGenres: string[];
  user1: {
    displayName: string;
    museUsername: string;
  };
  user2: {
    displayName: string;
    museUsername: string;
  };
}

export default function CompatibilityPage({ params }: { params: Promise<{ userId: string; friendId: string }> }) {
  const resolvedParams = use(params);
  const { profile, accessToken } = useUser();
  const [compatibilityData, setCompatibilityData] = useState<CompatibilityData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchCompatibility = async () => {
      if (!profile || !accessToken) return;
      
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/users/${resolvedParams.userId}/compatibility/${resolvedParams.friendId}`,
          {
            headers: {
              'access-token': accessToken
            }
          }
        );
        
        if (!response.ok) throw new Error('Failed to fetch compatibility');
        const data = await response.json();
        setCompatibilityData(data);
      } catch (error) {
        console.error('Error fetching compatibility:', error);
        setError('Failed to fetch compatibility data. Please try again later.');
      }
    };

    fetchCompatibility();
  }, [profile, accessToken, resolvedParams.userId, resolvedParams.friendId]);

  if (!profile) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-purple-900 to-black text-white">
        <Navigation />
        <div className="max-w-4xl mx-auto p-8 text-center">
          <p>Please log in to view compatibility.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-purple-900 to-black text-white">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => router.back()}
            className="mb-6 text-gray-400 hover:text-white flex items-center gap-2"
          >
            ← Back
          </button>

          <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
            <h1 className="text-3xl font-bold mb-8">Music Compatibility</h1>
            
            {error ? (
              <p className="text-red-400">{error}</p>
            ) : compatibilityData ? (
              <div className="space-y-8">
                <div className="text-center mb-8">
                  <div className="flex items-center justify-center gap-4 mb-6">
                    <div className="text-right">
                      <p className="font-medium text-lg">{compatibilityData.user1.displayName}</p>
                      <p className="text-gray-400">@{compatibilityData.user1.museUsername}</p>
                    </div>
                    <div className="text-2xl font-bold text-purple-500">vs</div>
                    <div className="text-left">
                      <p className="font-medium text-lg">{compatibilityData.user2.displayName}</p>
                      <p className="text-gray-400">@{compatibilityData.user2.museUsername}</p>
                    </div>
                  </div>
                  <div className="text-5xl font-bold text-purple-500 mb-4">
                    {compatibilityData.compatibilityScore}%
                  </div>
                  <p className="text-xl text-gray-300">
                    {compatibilityData.compatibilityScore >= 80 ? 'Excellent match! You have very similar music tastes.' :
                     compatibilityData.compatibilityScore >= 60 ? 'Good match! You share many musical interests.' :
                     compatibilityData.compatibilityScore >= 40 ? 'Moderate match. You have some common ground.' :
                     'Different tastes, but that can be interesting!'}
                  </p>
                </div>

                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-semibold mb-3">Shared Artists</h2>
                    {compatibilityData.commonArtists.length > 0 ? (
                      <ul className="space-y-2">
                        {compatibilityData.commonArtists.map((artist, index) => (
                          <li key={index} className="text-gray-300">{artist}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-400">No shared artists yet</p>
                    )}
                  </div>

                  <div>
                    <h2 className="text-xl font-semibold mb-3">Shared Genres</h2>
                    {compatibilityData.commonGenres.length > 0 ? (
                      <ul className="space-y-2">
                        {compatibilityData.commonGenres.map((genre, index) => (
                          <li key={index} className="text-gray-300">{genre}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-400">No shared genres yet</p>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
                <p className="text-gray-400">Loading compatibility data...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
} 