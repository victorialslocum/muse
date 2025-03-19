'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useUser } from '../contexts/UserContext';

export default function Navigation() {
  const { profile, logout } = useUser();
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (!profile) return null;

  const navigation = [
    { name: 'Profile', href: '/dashboard' },
    { name: 'Friends', href: '/friends' },
  ];

  return (
    <nav className="bg-black/20 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 text-xl font-bold text-purple-400">
              Muse
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                {navigation.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    className={`${
                      pathname === item.href
                        ? 'bg-purple-600 text-white'
                        : 'text-gray-300 hover:bg-purple-600/50 hover:text-white'
                    } rounded-md px-3 py-2 text-sm font-medium transition-colors`}
                  >
                    {item.name}
                  </a>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-300 text-sm hidden md:block">
              {profile.displayName}
            </span>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
            >
              Log Out
            </button>
          </div>
        </div>
        {/* Mobile navigation */}
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            {navigation.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className={`${
                  pathname === item.href
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-purple-600/50 hover:text-white'
                } block rounded-md px-3 py-2 text-base font-medium transition-colors`}
              >
                {item.name}
              </a>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
} 