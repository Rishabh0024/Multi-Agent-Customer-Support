import React from 'react';
import { KnowledgeManager } from '../components/Knowledge/KnowledgeManager';

export const KnowledgePage: React.FC = () => {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <KnowledgeManager />
    </div>
  );
};
