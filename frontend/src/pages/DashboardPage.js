import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function DashboardPage() {
    const { user, getAccessTokenSilently, isLoading: authLoading } = useAuth0();
    const [apiData, setApiData] = useState(null);
    const [apiLoading, setApiLoading] = useState(false);
    const [apiError, setApiError] = useState(null);

    useEffect(() => {
        const callSecureApi = async () => {
        if (!API_BASE_URL) {
            console.error("REACT_APP_API_BASE_URL is not defined in .env");
            setApiError("API endpoint not configured. Check frontend .env file.");
            return;
        }
        setApiLoading(true);
        setApiError(null);
        try {
            const token = await getAccessTokenSilently();
            const response = await axios.get(`${API_BASE_URL}/private`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
            });
            setApiData(response.data);
        } catch (error) {
            console.error('Error fetching data from API:', error);
            setApiError(
            error.response?.data?.description ||
            error.response?.data?.message || 
            error.message ||
            "Failed to fetch data from API."
            );
            setApiData(null);
        } finally {
            setApiLoading(false);
        }
        };

        if (!authLoading) {
            callSecureApi();
        }
    }, [getAccessTokenSilently, authLoading]);

    if (authLoading) {
        return <div className="page-loading">Loading user authentication...</div>;
    }

    return (
        <div className="page-container dashboard-page">
        <h2>Dashboard</h2>
        <p>Welcome back, {user?.name || user?.nickname || user?.email}!</p>

        <div className="profile-info">
            <h3>Your Auth0 Profile:</h3>
            <pre>{JSON.stringify(user, null, 2)}</pre>
        </div>

        <div className="api-data-section">
            <h3>Data from Secure API Endpoint (/api/profile):</h3>
            {apiLoading && <p>Loading data from API...</p>}
            {apiError && <p className="error-message">API Error: {apiError}</p>}
            {apiData && (
            <pre>{JSON.stringify(apiData, null, 2)}</pre>
            )}
            {!apiLoading && !apiError && !apiData && (
            <p>No data loaded from the API, or the endpoint might not be set up yet.</p>
            )}
        </div>
        </div>
    );
}

export default DashboardPage;