'use client';

import { useState } from 'react';
import { Plus, MessageSquare, Database, ChevronLeft, ChevronRight, Trash2, RefreshCw, Settings } from 'lucide-react';
import { useChatContext } from '@/lib/contexts/ChatContext';
import KnowledgeBaseManager from './KnowledgeBaseManager';

interface LeftSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export default function LeftSidebar({ isOpen, onToggle }: LeftSidebarProps) {
  const {
    conversations,
    currentConversation,
    selectedKbId,
    knowledgeBases,
    loadingKb,
    createNewConversation,
    selectConversation,
    selectKnowledgeBase,
    deleteConversation,
    refreshKnowledgeBases,
  } = useChatContext();

  const [showKbManager, setShowKbManager] = useState(false);

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

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
    <>
      <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Assistant</h2>
          <button
            onClick={onToggle}
            className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </button>
        </div>

        {/* New chat button */}
        <div className="p-4">
          <button 
            onClick={createNewConversation}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
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
            {conversations.length === 0 ? (
              <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                No conversation history yet
              </div>
            ) : (
              <div className="space-y-1">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`group relative p-2 rounded-lg transition-colors cursor-pointer ${
                      currentConversation?.id === conversation.id
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    <button
                      onClick={() => selectConversation(conversation.id)}
                      className="w-full text-left"
                    >
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{conversation.title}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {formatDate(conversation.updatedAt)}
                          </p>
                        </div>
                      </div>
                    </button>
                    
                    {/* Delete button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Are you sure you want to delete this conversation?')) {
                          deleteConversation(conversation.id);
                        }
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-all"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Knowledge base */}
          <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Knowledge base
              </h3>
              <div className="flex items-center gap-1">
                <button
                  onClick={refreshKnowledgeBases}
                  disabled={loadingKb}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-3 h-3 text-gray-500 dark:text-gray-400 ${loadingKb ? 'animate-spin' : ''}`} />
                </button>
                <button
                  onClick={() => setShowKbManager(true)}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <Settings className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                </button>
              </div>
            </div>
            
            {loadingKb ? (
              <div className="text-sm text-gray-500 dark:text-gray-400">Loading...</div>
            ) : knowledgeBases.length === 0 ? (
              <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-2">
                No knowledge base yet
              </div>
            ) : (
              <div className="space-y-1">
                <button
                  onClick={() => selectKnowledgeBase(undefined)}
                  className={`w-full text-left p-2 rounded-lg transition-colors ${
                    selectedKbId === undefined
                      ? 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">No knowledge base</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Answer based on general knowledge
                      </p>
                    </div>
                  </div>
                </button>
                
                {knowledgeBases.map((kb) => (
                  <button
                    key={kb.id}
                    onClick={() => selectKnowledgeBase(kb.id)}
                    className={`w-full text-left p-2 rounded-lg transition-colors ${
                      selectedKbId === kb.id
                        ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{kb.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {kb.file_count} files · {kb.vector_count} vectors
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

      {/* Knowledge Base Manager Modal */}
      <KnowledgeBaseManager 
        isOpen={showKbManager} 
        onClose={() => setShowKbManager(false)} 
      />
    </>
  );
} 