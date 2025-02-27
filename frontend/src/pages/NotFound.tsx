import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-6xl font-bold text-gray-800">404</h1>
      <p className="text-2xl text-gray-600 mb-6">Page not found</p>
      <Link to="/" className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
        Return to Dashboard
      </Link>
    </div>
  );
};

export default NotFound;