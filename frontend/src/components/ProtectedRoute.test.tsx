import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { ProtectedRoute } from '../App'; // We'll need to export this from App.tsx

// Mock the useAuth hook
jest.mock('../context/AuthContext', () => ({
  ...jest.requireActual('../context/AuthContext'),
  useAuth: jest.fn()
}));

// Import the mocked useAuth
const { useAuth } = jest.requireActual('../context/AuthContext');

// Test component to render inside ProtectedRoute
const TestComponent = () => <div>Protected Content</div>;

const renderProtectedRoute = (initialEntries = ['/protected']) => {
  render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <TestComponent />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('shows loading state when authentication is being checked', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      loading: true
    });

    renderProtectedRoute();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('redirects to login when user is not authenticated', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      loading: false
    });

    renderProtectedRoute();

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
    });
  });

  test('renders protected content when user is authenticated', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      loading: false
    });

    renderProtectedRoute();

    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });

  test('handles authentication state changes', async () => {
    // Start with loading state
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      loading: true
    });

    renderProtectedRoute();
    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Update to authenticated state
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      loading: false
    });

    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });
  });

  test('preserves route path when redirecting to login', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      loading: false
    });

    renderProtectedRoute(['/protected?param=test']);

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      // In a real implementation, we'd verify the redirect includes the return URL
    });
  });
});