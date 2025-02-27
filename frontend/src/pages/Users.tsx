import React from 'react';

const Users: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Users</h1>
      <p className="text-gray-600">Manage your users here.</p>
      
      {/* User list placeholder */}
      <div className="mt-6 bg-white shadow rounded-lg p-4">
        <p className="text-gray-500">User list will be displayed here.</p>
      </div>
    </div>
  );
};

export default Users;