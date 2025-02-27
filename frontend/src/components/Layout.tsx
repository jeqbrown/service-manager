import React from 'react';
import { Link, useLocation } from 'react-router-dom';

type LayoutProps = {
  children: React.ReactNode;
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path ? 'bg-indigo-800' : '';
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col h-0 flex-1 bg-indigo-900">
            <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
              <div className="flex items-center flex-shrink-0 px-4">
                <span className="text-white text-xl font-semibold">Service Manager</span>
              </div>
              <nav className="mt-5 flex-1 px-2 space-y-1">
                <Link to="/" className={`${isActive('/')} text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md`}>
                  Dashboard
                </Link>
                <Link to="/services" className={`${isActive('/services')} text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md`}>
                  Services
                </Link>
                <Link to="/users" className={`${isActive('/users')} text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md`}>
                  Users
                </Link>
                <Link to="/settings" className={`${isActive('/settings')} text-white group flex items-center px-2 py-2 text-sm font-medium rounded-md`}>
                  Settings
                </Link>
              </nav>
            </div>
            <div className="flex-shrink-0 flex border-t border-indigo-800 p-4">
              <div className="flex items-center">
                <div>
                  <div className="text-white text-sm font-medium">Admin User</div>
                  <button className="text-indigo-200 text-xs">Sign out</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile header */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <div className="md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3 flex items-center">
          <button className="text-gray-500 hover:text-gray-900">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <span className="ml-2 text-gray-900 text-lg font-medium">Service Manager</span>
        </div>
        
        {/* Main content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;