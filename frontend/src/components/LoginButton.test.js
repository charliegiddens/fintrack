import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { useAuth0 } from '@auth0/auth0-react';
import LoginButton from './LoginButton';

// Mock the useAuth0 hook
jest.mock('@auth0/auth0-react', () => ({
    useAuth0: jest.fn(),
}));

describe('LoginButton', () => {
    const mockLoginWithRedirect = jest.fn();

    beforeEach(() => {
        // Reset the mock before each test
        useAuth0.mockReturnValue({
            loginWithRedirect: mockLoginWithRedirect,
        });
    });

    afterEach(() => {
        // Clear mock calls after each test
        jest.clearAllMocks();
    });

    test('renders the login button', () => {
        render(<LoginButton />);
        const loginButton = screen.getByRole('button', { name: /Log In/i });
        expect(loginButton).toBeInTheDocument();
    });

    test('calls loginWithRedirect on button click', () => {
        render(<LoginButton />);
        const loginButton = screen.getByRole('button', { name: /Log In/i });

        fireEvent.click(loginButton);

        expect(mockLoginWithRedirect).toHaveBeenCalledTimes(1);
    });
});