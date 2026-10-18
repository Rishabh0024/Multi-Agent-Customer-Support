import React from 'react';
import { ChatWindow } from '../components/Chat/ChatWindow';

export const ChatPage: React.FC = () => {
  return (
    <div className="h-full w-full flex flex-col overflow-hidden">
      <ChatWindow />
    </div>
  );
};
