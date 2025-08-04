'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { KnowledgeBase } from '@/app/api/knowledge_base_api';

export interface Conversation {
  id: string;
  title: string;
  threadId: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}

interface ChatContextType {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  selectedKbId: string | undefined;
  
  knowledgeBases: KnowledgeBase[];
  loadingKb: boolean;
  
  createNewConversation: () => void;
  selectConversation: (id: string) => void;
  selectKnowledgeBase: (kbId: string | undefined) => void;
  addMessage: (conversationId: string, message: Message) => void;
  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => void;
  deleteConversation: (id: string) => void;
  refreshKnowledgeBases: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function useChatContext() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}

interface ChatProviderProps {
  children: ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [selectedKbId, setSelectedKbId] = useState<string | undefined>(undefined);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loadingKb, setLoadingKb] = useState(true);

  useEffect(() => {
    const savedConversations = localStorage.getItem('chat_conversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        const conversationsWithDates = parsed.map((conv: any) => ({
          ...conv,
          createdAt: new Date(conv.createdAt),
          updatedAt: new Date(conv.updatedAt),
          messages: conv.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }));
        setConversations(conversationsWithDates);
        
        if (conversationsWithDates.length > 0) {
          const latest = conversationsWithDates.reduce((latest: Conversation, current: Conversation) => 
            current.updatedAt > latest.updatedAt ? current : latest
          );
          setCurrentConversation(latest);
        }
      } catch (error) {
        console.error('Failed to load conversations from localStorage:', error);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('chat_conversations', JSON.stringify(conversations));
  }, [conversations]);

  const loadKnowledgeBases = async () => {
    try {
      setLoadingKb(true);
      const { getKnowledgeBases } = await import('@/app/api/knowledge_base_api');
      const knowledgeBases = await getKnowledgeBases();
      setKnowledgeBases(knowledgeBases);
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
    } finally {
      setLoadingKb(false);
    }
  };

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New conversation',
      threadId: crypto.randomUUID(),
      messages: [
        {
          id: '1',
          content: 'hello, I am your AI assistant, how can I help you?',
          role: 'assistant',
          timestamp: new Date(),
        }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversation(newConversation);
  };

  const selectConversation = (id: string) => {
    const conversation = conversations.find(c => c.id === id);
    if (conversation) {
      setCurrentConversation(conversation);
    }
  };

  const selectKnowledgeBase = (kbId: string | undefined) => {
    setSelectedKbId(kbId);
  };

  const addMessage = (conversationId: string, message: Message) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === conversationId) {
        const updatedConv = {
          ...conv,
          messages: [...conv.messages, message],
          updatedAt: new Date(),
        };
        
        if (message.role === 'user' && conv.messages.length === 1) {
          updatedConv.title = message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '');
        }
        
        return updatedConv;
      }
      return conv;
    }));

    if (currentConversation?.id === conversationId) {
      setCurrentConversation(prev => {
        if (!prev) return null;
        const updatedConv = {
          ...prev,
          messages: [...prev.messages, message],
          updatedAt: new Date(),
        };
        
        if (message.role === 'user' && prev.messages.length === 1) {
          updatedConv.title = message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '');
        }
        
        return updatedConv;
      });
    }
  };

  const updateMessage = useCallback((conversationId: string, messageId: string, updates: Partial<Message>) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === conversationId) {
        return {
          ...conv,
          messages: conv.messages.map(msg => 
            msg.id === messageId ? { ...msg, ...updates } : msg
          ),
          updatedAt: new Date(),
        };
      }
      return conv;
    }));

    if (currentConversation?.id === conversationId) {
      setCurrentConversation(prev => {
        if (!prev) return null;
        return {
          ...prev,
          messages: prev.messages.map(msg => 
            msg.id === messageId ? { ...msg, ...updates } : msg
          ),
          updatedAt: new Date(),
        };
      });
    }
  }, [currentConversation]);

  const deleteConversation = (id: string) => {
    setConversations(prev => prev.filter(conv => conv.id !== id));
    
    if (currentConversation?.id === id) {
      const remainingConversations = conversations.filter(conv => conv.id !== id);
      if (remainingConversations.length > 0) {
        setCurrentConversation(remainingConversations[0]);
      } else {
        setCurrentConversation(null);
      }
    }
  };

  const refreshKnowledgeBases = async () => {
    await loadKnowledgeBases();
  };

  const value: ChatContextType = {
    conversations,
    currentConversation,
    selectedKbId,
    knowledgeBases,
    loadingKb,
    createNewConversation,
    selectConversation,
    selectKnowledgeBase,
    addMessage,
    updateMessage,
    deleteConversation,
    refreshKnowledgeBases,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
} 