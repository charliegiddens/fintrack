import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { useAuth0 } from '@auth0/auth0-react';
import LogoutButton from './LogoutButton';

// Mock the useAuth0 hook
jest.mock('@auth0/auth0-react', () => ({
    useAuth0: jest.fn(),
}));

describe('LogoutButton', () => {
    const mockLogout = jest.fn();

    beforeEach(() => {
        // Reset the mock before each test and provide the logout function
        useAuth0.mockReturnValue({
            logout: mockLogout,
            // You might need isAuthenticated: true here if your LogoutButton
            // was conditionally rendered based on authentication status,
            // but based on the component code provided, it's not.
        });
    });

    afterEach(() => {
        // Clear mock calls after each test
        jest.clearAllMocks();
    });

    test('renders the logout button', () => {
        render(<LogoutButton />);
        const logoutButton = screen.getByRole('button', { name: /Log Out/i });
        expect(logoutButton).toBeInTheDocument();
    });

    test('calls logout with correct parameters on button click', () => {
        // Define the expected returnTo value
        const expectedReturnTo = window.location.origin;

        render(<LogoutButton />);
        const logoutButton = screen.getByRole('button', { name: /Log Out/i });

        fireEvent.click(logoutButton);

        // Verify that mockLogout was called once with the specific parameters
        expect(mockLogout).toHaveBeenCalledTimes(1);
        expect(mockLogout).toHaveBeenCalledWith({
            logoutParams: {
                returnTo: expectedReturnTo,
            },
        });
    });
});