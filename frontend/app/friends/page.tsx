'use client';

import { useEffect, useState } from 'react';
import { useUser } from '../contexts/UserContext';
import Navigation from '../components/Navigation';
import { useRouter } from 'next/navigation';

interface Friend {
  displayName: string;
  museUsername: string;
  spotifyId: string;
  profileImageUrl: string;
}

export default function Friends() {
  const { profile, accessToken } = useUser();
  const [friends, setFriends] = useState<Friend[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Friend[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadFriends();
  }, [profile, accessToken]);

  const loadFriends = async () => {
    if (!profile || !accessToken) return;
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/friends/${profile.spotifyId}`, {
        headers: {
          'access-token': accessToken
        }
      });
      if (!response.ok) throw new Error('Failed to fetch friends');
      const data = await response.json();
      setFriends(data);
    } catch (error) {
      console.error('Error loading friends:', error);
      setError('Failed to load friends. Please try again later.');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || !accessToken) return;
    
    setIsSearching(true);
    setError(null);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/search?username=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'access-token': accessToken
        }
      });
      if (!response.ok) throw new Error('Failed to search users');
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Error searching users:', error);
      setError('Failed to search users. Please try again later.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddFriend = async (friendUsername: string) => {
    if (!profile || !accessToken) return;
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/friends/${profile.spotifyId}/${friendUsername}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'access-token': accessToken
        }
      });
      
      if (!response.ok) throw new Error('Failed to add friend');
      
      // Refresh friends list
      loadFriends();
      // Clear search results
      setSearchResults([]);
      setSearchQuery('');
    } catch (error) {
      console.error('Error adding friend:', error);
      setError('Failed to add friend. Please try again later.');
    }
  };

  const handleRemoveFriend = async (friendUsername: string) => {
    if (!profile || !accessToken) return;
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/friends/${profile.spotifyId}/${friendUsername}`, {
        method: 'DELETE',
        headers: {
          'access-token': accessToken
        }
      });
      
      if (!response.ok) throw new Error('Failed to remove friend');
      
      // Refresh friends list
      loadFriends();
    } catch (error) {
      console.error('Error removing friend:', error);
      setError('Failed to remove friend. Please try again later.');
    }
  };

  const handleFriendClick = (friend: Friend) => {
    if (!profile) return;
    router.push(`/compatibility/${profile.spotifyId}/${friend.spotifyId}`);
  };

  if (!profile) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-purple-900 to-black text-white">
        <Navigation />
        <div className="max-w-4xl mx-auto p-8 text-center">
          <p>Please log in to view and manage your friends.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-purple-900 to-black text-white">
      <Navigation />
      
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Friends</h1>
        
        {/* Search Section */}
        <div className="mb-8">
          <div className="flex gap-4 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by username"
              className="flex-1 bg-white/10 rounded-lg px-4 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="bg-white/5 rounded-lg p-4 backdrop-blur-sm">
              <h2 className="text-xl font-semibold mb-4">Search Results</h2>
              <div className="space-y-4">
                {searchResults.map((user) => (
                  <div key={user.spotifyId} className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <img
                        src={user.profileImageUrl}
                        alt={user.displayName}
                        className="w-12 h-12 rounded-full"
                      />
                      <div>
                        <p className="font-medium">{user.displayName}</p>
                        <p className="text-gray-400">@{user.museUsername}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleAddFriend(user.museUsername)}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                      Add Friend
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Friends List */}
        <div className="bg-white/5 rounded-lg p-6 backdrop-blur-sm">
          <h2 className="text-xl font-semibold mb-4">Your Friends</h2>
          {error && (
            <p className="text-red-400 mb-4">{error}</p>
          )}
          {friends.length === 0 ? (
            <p className="text-gray-400">No friends added yet.</p>
          ) : (
            <div className="space-y-4">
              {friends.map((friend) => (
                <div
                  key={friend.spotifyId}
                  className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                  onClick={() => handleFriendClick(friend)}
                >
                  <div className="flex items-center gap-4">
                    <img
                      src={friend.profileImageUrl || '/default-avatar.png'}
                      alt={friend.displayName}
                      className="w-12 h-12 rounded-full"
                    />
                    <div>
                      <p className="font-medium">{friend.displayName}</p>
                      <p className="text-gray-400">@{friend.museUsername}</p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveFriend(friend.museUsername);
                    }}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
} 