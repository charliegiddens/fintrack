import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import LoginButton from '../components/LoginButton';

function HomePage() {
    const { isAuthenticated, user, isLoading } = useAuth0();

    if (isLoading) {
        return <div className="page-loading">Loading...</div>;
    }

    return (
        <div className="page-container home-page">
        <h1>Welcome to FinTrack</h1>
        {!isAuthenticated && (
        <>
            <p>Please log in to manage your finances and track your expenses.</p>
            <LoginButton />
        </>
        )}
        {isAuthenticated && (
            <p>
                Hello, {user?.name || user?.nickname || user?.email || 'Valued User'}! You are successfully logged in.
            </p>
        )}
    </div>
    );
}

export default HomePage;