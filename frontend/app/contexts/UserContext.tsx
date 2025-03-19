'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface UserProfile {
  spotifyId: string;
  displayName: string;
  museUsername: string;
  topArtists: string[];
  topGenres: string[];
  recentTracks: string[];
}

interface UserContextType {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  accessToken: string | null;
  login: (accessToken: string) => Promise<void>;
  logout: () => void;
  updateUsername: (newUsername: string) => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    // Try to get token from localStorage on mount
    const storedToken = localStorage.getItem('accessToken');
    if (storedToken) {
      login(storedToken).catch(() => {
        // If login fails, clear the stored token
        localStorage.removeItem('accessToken');
      });
    }
  }, []);

  const login = async (token: string) => {
    setIsLoading(true);
    setError(null);
    setAccessToken(token);
    localStorage.setItem('accessToken', token);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/profile`, {
        headers: {
          'access-token': token
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch profile');
      }

      const data = await response.json();
      setProfile(data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      setError('Failed to fetch profile');
      setAccessToken(null);
      localStorage.removeItem('accessToken');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setProfile(null);
    setAccessToken(null);
    setError(null);
    localStorage.removeItem('accessToken');
  };

  const updateUsername = async (newUsername: string) => {
    if (!profile || !accessToken) return;
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/users/profile/${profile.spotifyId}/username`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'access-token': accessToken
          },
          body: JSON.stringify({ new_username: newUsername }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to update username');
      }

      // Update local profile with new username
      setProfile({ ...profile, museUsername: newUsername });
    } catch (error) {
      console.error('Error updating username:', error);
      throw error;
    }
  };

  return (
    <UserContext.Provider value={{ profile, isLoading, error, accessToken, login, logout, updateUsername }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
} 