import React from 'react';
import { KnowledgeManager } from '../components/Knowledge/KnowledgeManager';

export const KnowledgePage: React.FC = () => {
  return (
    <div className="mx-auto max-w-7xl px-3 py-3.5 sm:px-6 sm:py-6">
      <KnowledgeManager />
    </div>
  );
};
