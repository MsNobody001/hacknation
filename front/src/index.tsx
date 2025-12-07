import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ContextProvider } from './context';

import './index.css';
import { App } from './components';
import { hasSession, initSession } from './session';

const container = document.getElementById('root');
const root = createRoot(container!);

if (!hasSession()) initSession();

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ContextProvider>
        <App />
      </ContextProvider>
    </BrowserRouter>
  </React.StrictMode>
);
