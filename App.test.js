import { render, screen } from '@testing-library/react';
import App from './App';
import { BrowserRouter as Router } from 'react-router-dom';

test('renders welcome message on home page', () => {
  render(
    <Router>
      <App />
    </Router>
  );
  const heading = screen.getByText(/job application tracker/i);
  expect(heading).toBeInTheDocument();
});

test('renders login page heading', () => {
  render(
    <Router>
      <App />
    </Router>
  );
  // Navigate to /login manually since routing logic isn't triggered automatically in this test
  window.history.pushState({}, 'Login Page', '/login');
  const loginHeading = screen.queryByText(/login/i);
  expect(loginHeading).toBeInTheDocument();
});
