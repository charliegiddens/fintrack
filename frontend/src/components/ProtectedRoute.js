import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

const ProtectedRoute = ({ component: Component, ...rest }) => {
    const { isAuthenticated, isLoading } = useAuth0();

    if (isLoading) {
        return <div className="page-loading">Loading authentication status...</div>;
    }

    return isAuthenticated ? <Component {...rest} /> : <Navigate to="/" replace />;
};

export default ProtectedRoute;