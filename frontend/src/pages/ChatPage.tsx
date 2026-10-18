import React from 'react';
import { ChatWindow } from '../components/Chat/ChatWindow';

export const ChatPage: React.FC = () => {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6">
      <ChatWindow />
    </div>
  );
};
