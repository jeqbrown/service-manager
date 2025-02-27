import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { format } from 'date-fns';

interface WorkOrder {
  id: number;
  title: string;
  status: string;
  customer: string;
}

interface UpcomingService {
  id: number;
  date: string;
  type: string;
  customer: string;
}

interface DashboardData {
  recentWorkOrders: WorkOrder[];
  statistics: {
    totalWorkOrders: number;
    pendingServices: number;
    completedToday: number;
    activeCustomers: number;
  };
  upcomingServices: UpcomingService[];
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData | null>(null);
  const [dateRange, setDateRange] = useState({
    startDate: format(new Date(), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd')
  });

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/dashboard', {
        params: {
          startDate: dateRange.startDate,
          endDate: dateRange.endDate
        }
      });
      setData(response.data);
    } catch (err) {
      setError('Error loading dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [dateRange.startDate, dateRange.endDate]);

  if (loading) {
    return (
      <div data-testid="dashboard-loading" className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <input
              type="date"
              data-testid="date-range-start"
              value={dateRange.startDate}
              onChange={(e) => setDateRange(prev => ({ ...prev, startDate: e.target.value }))}
              className="border rounded px-2 py-1"
            />
            <span>to</span>
            <input
              type="date"
              data-testid="date-range-end"
              value={dateRange.endDate}
              onChange={(e) => setDateRange(prev => ({ ...prev, endDate: e.target.value }))}
              className="border rounded px-2 py-1"
            />
          </div>
          <button
            data-testid="refresh-button"
            onClick={fetchDashboardData}
            className="bg-primary text-white p-2 rounded hover:bg-primary-dark"
          >
            <RefreshIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Total Work Orders"
          value={data?.statistics.totalWorkOrders}
          icon={<DocumentIcon />}
        />
        <StatCard
          title="Pending Services"
          value={data?.statistics.pendingServices}
          icon={<ClockIcon />}
        />
        <StatCard
          title="Completed Today"
          value={data?.statistics.completedToday}
          icon={<CheckIcon />}
        />
        <StatCard
          title="Active Customers"
          value={data?.statistics.activeCustomers}
          icon={<UsersIcon />}
        />
      </div>

      {/* Recent Work Orders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Work Orders</h2>
          <div className="space-y-4">
            {data?.recentWorkOrders.map((order) => (
              <div
                key={order.id}
                onClick={() => navigate(`/work-orders/${order.id}`)}
                className="p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium">{order.title}</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    order.status === 'completed' ? 'bg-green-100 text-green-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {order.status}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mt-1">{order.customer}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Upcoming Services */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Upcoming Services</h2>
          <div className="space-y-4">
            {data?.upcomingServices.map((service) => (
              <div key={service.id} className="p-4 border rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{service.type}</span>
                  <span className="text-gray-600">
                    {format(new Date(service.date), 'MMM dd, yyyy')}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mt-1">{service.customer}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value?: number;
  icon: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center justify-between">
      <div className="text-gray-500">{icon}</div>
      <div className="text-right">
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-gray-500 text-sm">{title}</div>
      </div>
    </div>
  </div>
);

// Icons components (you can replace these with your icon library)
const RefreshIcon = () => (
  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const DocumentIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const ClockIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CheckIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const UsersIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

export default Dashboard;
