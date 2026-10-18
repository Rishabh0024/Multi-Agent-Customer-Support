import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { ChatPage } from './pages/ChatPage';
import { TicketsPage } from './pages/TicketsPage';
import { KnowledgePage } from './pages/KnowledgePage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="h-[100dvh] max-h-[100dvh] w-full flex flex-col overflow-hidden bg-slate-50 text-slate-800">
        <Navbar />
        <main className="flex-1 flex flex-col overflow-hidden relative pb-14 md:pb-0">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route
              path="/tickets"
              element={
                <div className="flex-1 overflow-y-auto">
                  <TicketsPage />
                </div>
              }
            />
            <Route
              path="/knowledge"
              element={
                <div className="flex-1 overflow-y-auto">
                  <KnowledgePage />
                </div>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
