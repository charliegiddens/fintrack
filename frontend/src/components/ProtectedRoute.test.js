import React from 'react';
import { render, screen } from '@testing-library/react';
import { useAuth0 } from '@auth0/auth0-react';
import ProtectedRoute from './ProtectedRoute';
import PropTypes from 'prop-types'; // Import PropTypes if not already available globally in tests

// Mock the useAuth0 hook
jest.mock('@auth0/auth0-react', () => ({
    useAuth0: jest.fn(),
}));

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => {
    const actual = jest.requireActual('react-router-dom');
    return {
        ...actual,
        Navigate: (props) => {
            mockNavigate(props);
            return null;
            },
    };
});

// Define a simple dummy component for testing
const MockProtectedComponent = ({ extraProp }) => (
    <div>
        Protected Content {extraProp}
    </div>
);
MockProtectedComponent.propTypes = {
    extraProp: PropTypes.string,
};


describe('ProtectedRoute', () => {
    const mockUseAuth0 = useAuth0;

    beforeEach(() => {
        // Clear mocks before each test
        jest.clearAllMocks();
    });

    test('renders loading message when isLoading is true', () => {
        mockUseAuth0.mockReturnValue({
            isAuthenticated: false,
            isLoading: true,
        });

        render(<ProtectedRoute component={MockProtectedComponent} />);

        expect(screen.getByText(/Loading authentication status.../i)).toBeInTheDocument();
        expect(mockNavigate).not.toHaveBeenCalled(); // Navigate should not be called when loading
        expect(screen.queryByText(/Protected Content/i)).not.toBeInTheDocument(); // Protected component should not be rendered
    });

    test('renders the protected component when isAuthenticated is true and not loading', () => {
        mockUseAuth0.mockReturnValue({
            isAuthenticated: true,
            isLoading: false,
        });

        const extraPropValue = "some value";
        render(<ProtectedRoute component={MockProtectedComponent} extraProp={extraPropValue} />);

        expect(screen.queryByText(/Loading authentication status.../i)).not.toBeInTheDocument();
        expect(mockNavigate).not.toHaveBeenCalled(); // Navigate should not be called when authenticated
        expect(screen.getByText(`Protected Content ${extraPropValue}`)).toBeInTheDocument(); // Protected component should be rendered with props
    });

    test('redirects to home when isAuthenticated is false and not loading', () => {
        mockUseAuth0.mockReturnValue({
            isAuthenticated: false,
            isLoading: false,
        });

        render(<ProtectedRoute component={MockProtectedComponent} />);

        expect(screen.queryByText(/Loading authentication status.../i)).not.toBeInTheDocument();
        expect(screen.queryByText(/Protected Content/i)).not.toBeInTheDocument(); // Protected component should not be rendered

        // Check if the mocked Navigate component was called with the correct props
        expect(mockNavigate).toHaveBeenCalledTimes(1);
        expect(mockNavigate).toHaveBeenCalledWith({ to: '/', replace: true }); // Check the props passed to Navigate
    });
});