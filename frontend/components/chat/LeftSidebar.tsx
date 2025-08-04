'use client';

import { useState, useEffect } from 'react';
import { Plus, MessageSquare, Database, ChevronLeft, ChevronRight } from 'lucide-react';
import { getKnowledgeBases, KnowledgeBase } from '@/app/api/chat_api';

interface LeftSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export default function LeftSidebar({ isOpen, onToggle }: LeftSidebarProps) {
  const [selectedChat, setSelectedChat] = useState<string | null>(null);
  const [selectedKb, setSelectedKb] = useState<string | null>(null);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const chatHistory = [
    { id: '1', title: 'Conversation 1', timestamp: '2024-01-15' },
    { id: '2', title: 'Conversation 2', timestamp: '2024-01-14' },
    { id: '3', title: 'Conversation 3', timestamp: '2024-01-13' },
  ];

  useEffect(() => {
    const fetchKnowledgeBases = async () => {
      try {
        setLoading(true);
        const response = await getKnowledgeBases();
        setKnowledgeBases(response.knowledge_bases);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch knowledge bases:', err);
        setError('Failed to fetch knowledge bases');
      } finally {
        setLoading(false);
      }
    };

    fetchKnowledgeBases();
  }, []);

  if (!isOpen) {
    return (
      <div className="w-12 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center py-4">
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        </button>
      </div>
    );
  }

  return (
    <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI 助手</h2>
        <button
          onClick={onToggle}
          className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-gray-300" />
        </button>
      </div>

      {/* New chat button */}
      <div className="p-4">
        <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
          <Plus className="w-4 h-4" />
          New chat
        </button>
      </div>

      {/* Conversation history */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-2">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
            Conversation history
          </h3>
          <div className="space-y-1">
            {chatHistory.map((chat) => (
              <button
                key={chat.id}
                onClick={() => setSelectedChat(chat.id)}
                className={`w-full text-left p-2 rounded-lg transition-colors ${
                  selectedChat === chat.id
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{chat.title}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{chat.timestamp}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Knowledge base */}
        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
            Knowledge base
          </h3>
          {loading ? (
            <div className="text-sm text-gray-500 dark:text-gray-400">加载中...</div>
          ) : error ? (
            <div className="text-sm text-red-500 dark:text-red-400">{error}</div>
          ) : (
            <div className="space-y-1">
              {knowledgeBases.map((kb) => (
                <button
                  key={kb.id}
                  onClick={() => setSelectedKb(kb.id)}
                  className={`w-full text-left p-2 rounded-lg transition-colors ${
                    selectedKb === kb.id
                      ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{kb.name}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {kb.file_count} 文件 · {kb.vector_count} 向量
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 