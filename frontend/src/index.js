import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { Auth0Provider } from '@auth0/auth0-react';

const domain = process.env.REACT_APP_AUTH0_DOMAIN;
const clientId = process.env.REACT_APP_AUTH0_CLIENT_ID;
const audience = process.env.REACT_APP_AUTH0_API_AUDIENCE;

if (!domain || !clientId || !audience) {
  console.error(
    'Auth0 configuration is missing. Please check your .env file and ensure variables are prefixed with REACT_APP_ (e.g., REACT_APP_AUTH0_DOMAIN).'
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: audience,
        // scope: "openid profile email read:expenses"
      }}
    >
      <App />
    </Auth0Provider>
  </React.StrictMode>
);