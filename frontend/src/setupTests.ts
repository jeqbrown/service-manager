// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Suppress React Router future flag warnings in tests
jest.mock('react-router', () => {
  const originalModule = jest.requireActual('react-router');
  return {
    ...originalModule,
    UNSAFE_useScrollRestoration: jest.fn(),
    UNSAFE_usePrompt: jest.fn(),
  };
});

// This suppresses console warnings in tests
const originalWarn = console.warn;
console.warn = (...args) => {
  // Filter out React Router future flag warnings
  if (args[0] && typeof args[0] === 'string' && args[0].includes('React Router Future Flag Warning')) {
    return;
  }
  originalWarn(...args);
};
