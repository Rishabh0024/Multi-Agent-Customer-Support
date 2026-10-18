import React, { useState } from 'react';
import { BookOpen, Plus, Trash2, Search, Sparkles, Database, X } from 'lucide-react';
import { useKnowledgeDocs, useIndexKnowledgeDoc, useDeleteKnowledgeDoc, apiClient } from '../../services/api';

export const KnowledgeManager: React.FC = () => {
  const { data: docs, isLoading } = useKnowledgeDocs();
  const indexMutation = useIndexKnowledgeDoc();
  const deleteMutation = useDeleteKnowledgeDoc();

  const [isAdding, setIsAdding] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('Returns & Refunds');
  const [newContent, setNewContent] = useState('');

  // Semantic search test state
  const [testQuery, setTestQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleAddDocument = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;

    indexMutation.mutate(
      {
        title: newTitle.trim(),
        category: newCategory,
        content: newContent.trim(),
      },
      {
        onSuccess: () => {
          setNewTitle('');
          setNewContent('');
          setIsAdding(false);
        },
      }
    );
  };

  const handleTestSearch = async () => {
    if (!testQuery.trim()) return;
    setIsSearching(true);
    try {
      const { data } = await apiClient.post('/api/knowledge/search', {
        query: testQuery.trim(),
        limit: 4,
      });
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Action */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div>
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-sky-600" />
            Knowledge Base & RAG Index
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Documents stored in PostgreSQL and vectorized in Qdrant for semantic similarity retrieval.
          </p>
        </div>

        <button
          onClick={() => setIsAdding(!isAdding)}
          className="flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-sky-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>{isAdding ? 'Cancel' : 'Add New Document'}</span>
        </button>
      </div>

      {/* Add Document Form */}
      {isAdding && (
        <form
          onSubmit={handleAddDocument}
          className="rounded-2xl border border-sky-200 bg-sky-50/50 p-5 shadow-sm space-y-4"
        >
          <h3 className="text-sm font-bold text-sky-900">Index New Support Knowledge</h3>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="text-xs font-semibold text-slate-700">Document Title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g., International Shipping Guidelines"
                className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-xs text-slate-800 focus:border-sky-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700">Category</label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-xs text-slate-800 focus:border-sky-500 focus:outline-none"
              >
                <option value="Returns & Refunds">Returns & Refunds</option>
                <option value="Shipping & Logistics">Shipping & Logistics</option>
                <option value="Warranty & Repairs">Warranty & Repairs</option>
                <option value="Orders & Billing">Orders & Billing</option>
                <option value="Account & Security">Account & Security</option>
                <option value="General">General</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700">Document Content (Text)</label>
            <textarea
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="Paste policy text or FAQs here..."
              rows={4}
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-2.5 text-xs text-slate-800 focus:border-sky-500 focus:outline-none"
              required
            />
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={indexMutation.isPending}
              className="rounded-lg bg-sky-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-sky-700 disabled:opacity-50"
            >
              {indexMutation.isPending ? 'Vectorizing in Qdrant...' : 'Save & Vectorize'}
            </button>
          </div>
        </form>
      )}

      {/* Semantic Search Interactive Playground */}
      <div className="rounded-2xl border border-indigo-100 bg-gradient-to-r from-indigo-50/70 to-purple-50/70 p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="h-4 w-4 text-indigo-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-900">
            Live Qdrant Vector Search Playground
          </h3>
        </div>
        <p className="text-xs text-slate-500 mb-3">
          Type any query to test cosine similarity scoring in Qdrant:
        </p>

        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleTestSearch()}
              placeholder="e.g. Can I return opened boxes within 30 days?"
              className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-xs text-slate-800 focus:border-indigo-500 focus:outline-none pr-8"
            />
            {testQuery && (
              <button
                type="button"
                onClick={() => {
                  setTestQuery('');
                  setSearchResults(null);
                }}
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <button
            onClick={handleTestSearch}
            disabled={isSearching || !testQuery.trim()}
            className="flex items-center justify-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            <Search className="h-4 w-4" />
            <span>{isSearching ? 'Searching...' : 'Search Qdrant'}</span>
          </button>
        </div>

        {/* Search Results Display */}
        {searchResults && (
          <div className="mt-4 space-y-2 border-t border-indigo-100 pt-3">
            <h4 className="text-xs font-semibold text-indigo-900">
              Top Ranked Matches ({searchResults.length}):
            </h4>
            {searchResults.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No matches above threshold.</p>
            ) : (
              searchResults.map((hit, idx) => (
                <div
                  key={idx}
                  className="rounded-xl border border-indigo-100 bg-white p-3 shadow-xs flex items-start justify-between gap-4"
                >
                  <div>
                    <span className="font-semibold text-slate-800 text-xs block">{hit.title}</span>
                    <span className="text-[10px] text-slate-400 block mb-1">Category: {hit.category}</span>
                    <p className="text-xs text-slate-600 line-clamp-2">{hit.content}</p>
                  </div>
                  <span className="rounded-md bg-indigo-100 px-2 py-0.5 text-xs font-bold text-indigo-700 shrink-0">
                    Score: {(hit.score * 100).toFixed(1)}%
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Indexed Documents Grid */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
          <Database className="h-4 w-4 text-slate-500" />
          Indexed Articles in PostgreSQL & Qdrant ({docs?.length ?? 0})
        </h3>

        {isLoading ? (
          <div className="text-center py-8 text-xs text-slate-400">Loading documents...</div>
        ) : !docs || docs.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">No documents found.</div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {docs.map((doc) => (
              <div
                key={doc.id}
                className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-xs hover:border-slate-300 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="rounded bg-sky-50 px-2 py-0.5 text-[11px] font-semibold text-sky-700">
                      {doc.category}
                    </span>
                    <button
                      onClick={() => deleteMutation.mutate(doc.id)}
                      className="text-slate-400 hover:text-rose-600 transition-colors"
                      title="Delete from DB & Qdrant"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <h4 className="text-sm font-bold text-slate-800 mb-1">{doc.title}</h4>
                  <p className="text-xs text-slate-600 line-clamp-4 leading-relaxed">
                    {doc.content}
                  </p>
                </div>
                <div className="mt-3 border-t border-slate-100 pt-2 text-[10px] text-slate-400 font-mono">
                  ID: {doc.id}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
