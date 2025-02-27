import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import Dashboard from './Dashboard';
import api from '../services/api';
import MockAdapter from 'axios-mock-adapter';

const mockApi = new MockAdapter(api);

// Mock data representing the expected API response structure
const mockDashboardData = {
  recentWorkOrders: [
    { id: 1, title: 'Repair AC Unit', status: 'pending', customer: 'John Doe' },
    { id: 2, title: 'Install Heater', status: 'completed', customer: 'Jane Smith' }
  ],
  statistics: {
    totalWorkOrders: 150,
    pendingServices: 45,
    completedToday: 12,
    activeCustomers: 89
  },
  upcomingServices: [
    { id: 1, date: '2024-03-20', type: 'Maintenance', customer: 'Tech Corp' },
    { id: 2, date: '2024-03-21', type: 'Installation', customer: 'ABC Inc' }
  ]
};

// Helper function to render the Dashboard component with required providers
const renderDashboard = () => {
  render(
    <MemoryRouter>
      <AuthProvider>
        <Dashboard />
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Dashboard', () => {
  beforeEach(() => {
    mockApi.reset();
    localStorage.clear();
  });

  // Test Suite 1: Loading State
  describe('Loading State', () => {
    test('shows loading state while fetching data', async () => {
      // Simulate delayed API response to test loading state
      mockApi.onGet('/dashboard').reply(() => {
        return new Promise(resolve => setTimeout(() => resolve([200, mockDashboardData]), 100));
      });

      renderDashboard();

      // Verify loading indicator is shown
      expect(screen.getByTestId('dashboard-loading')).toBeInTheDocument();
      
      // Verify loading indicator is removed after data loads
      await waitFor(() => {
        expect(screen.queryByTestId('dashboard-loading')).not.toBeInTheDocument();
      });
    });
  });

  // Test Suite 2: Data Display
  describe('Data Display', () => {
    beforeEach(() => {
      mockApi.onGet('/dashboard').reply(200, mockDashboardData);
    });

    test('displays statistics cards correctly', async () => {
      renderDashboard();

      // Verify all statistics are displayed
      await waitFor(() => {
        expect(screen.getByText('150')).toBeInTheDocument(); // Total Work Orders
        expect(screen.getByText('45')).toBeInTheDocument(); // Pending Services
        expect(screen.getByText('12')).toBeInTheDocument(); // Completed Today
        expect(screen.getByText('89')).toBeInTheDocument(); // Active Customers
      });
    });

    test('displays recent work orders', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Repair AC Unit')).toBeInTheDocument();
        expect(screen.getByText('Install Heater')).toBeInTheDocument();
      });
    });

    test('displays upcoming services', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Tech Corp')).toBeInTheDocument();
        expect(screen.getByText('ABC Inc')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('displays error message when API call fails', async () => {
      mockApi.onGet('/dashboard').reply(500, { message: 'Internal Server Error' });

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText(/error loading dashboard data/i)).toBeInTheDocument();
      });
    });

    test('shows retry button when data loading fails', async () => {
      mockApi.onGet('/dashboard').reply(500);

      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText(/retry/i)).toBeInTheDocument();
      });

      // Setup success response for retry
      mockApi.onGet('/dashboard').reply(200, mockDashboardData);

      // Click retry button
      fireEvent.click(screen.getByText(/retry/i));

      await waitFor(() => {
        expect(screen.getByText('150')).toBeInTheDocument(); // Verify data loaded
      });
    });
  });

  describe('Interactions', () => {
    beforeEach(() => {
      mockApi.onGet('/dashboard').reply(200, mockDashboardData);
    });

    test('work order click navigates to detail view', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('Repair AC Unit')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Repair AC Unit'));
      
      // Verify navigation (you'll need to implement this based on your routing setup)
      expect(window.location.pathname).toContain('/work-orders/1');
    });

    test('refresh button fetches new data', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('150')).toBeInTheDocument();
      });

      // Setup new data for refresh
      const newData = {
        ...mockDashboardData,
        statistics: { ...mockDashboardData.statistics, totalWorkOrders: 155 }
      };
      mockApi.onGet('/dashboard').reply(200, newData);

      // Click refresh button
      fireEvent.click(screen.getByTestId('refresh-button'));

      await waitFor(() => {
        expect(screen.getByText('155')).toBeInTheDocument();
      });
    });
  });

  describe('Filters and Search', () => {
    test('date range filter updates dashboard data', async () => {
      renderDashboard();

      await waitFor(() => {
        expect(screen.getByText('150')).toBeInTheDocument();
      });

      // Setup filtered data response
      const filteredData = {
        ...mockDashboardData,
        statistics: { ...mockDashboardData.statistics, totalWorkOrders: 50 }
      };
      mockApi.onGet('/dashboard', { params: { startDate: '2024-03-01', endDate: '2024-03-31' } })
        .reply(200, filteredData);

      // Set date range
      fireEvent.change(screen.getByTestId('date-range-start'), {
        target: { value: '2024-03-01' }
      });
      fireEvent.change(screen.getByTestId('date-range-end'), {
        target: { value: '2024-03-31' }
      });

      await waitFor(() => {
        expect(screen.getByText('50')).toBeInTheDocument();
      });
    });
  });
});
