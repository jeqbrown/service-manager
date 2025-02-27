import React from 'react';
import { Link } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: 'home' },
    { name: 'Services', path: '/services', icon: 'server' },
    { name: 'Users', path: '/users', icon: 'users' },
    { name: 'Settings', path: '/settings', icon: 'cog' },
  ];

  return (
    <div className="bg-gray-800 text-white w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform -translate-x-full md:relative md:translate-x-0 transition duration-200 ease-in-out">
      <div className="flex items-center space-x-4 px-4">
        <span className="text-2xl font-extrabold">SM</span>
        <span>Service Manager</span>
      </div>
      <nav>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700"
          >
            {item.name}
          </Link>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;