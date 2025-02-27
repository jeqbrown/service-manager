import React from 'react';

const Services: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Services</h1>
      <p className="text-gray-600">Manage your services here.</p>
      
      {/* Services list placeholder */}
      <div className="mt-6 bg-white shadow rounded-lg p-4">
        <p className="text-gray-500">Service list will be displayed here.</p>
      </div>
    </div>
  );
};

export default Services;
