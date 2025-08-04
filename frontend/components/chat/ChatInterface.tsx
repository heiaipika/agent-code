'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Menu, User, Bot, Loader2, Plus } from 'lucide-react';
import { streamChat, ChatResponse } from '@/app/api/chat_api';
import { useChatContext, Message } from '@/lib/contexts/ChatContext';

interface ChatInterfaceProps {
  onToggleLeftSidebar: () => void;
}

export default function ChatInterface({ onToggleLeftSidebar }: ChatInterfaceProps) {
  const {
    currentConversation,
    selectedKbId,
    addMessage,
    updateMessage,
    createNewConversation,
  } = useChatContext();

  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [assistantMessageContent, setAssistantMessageContent] = useState('');
  const [currentAssistantMessageId, setCurrentAssistantMessageId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentConversation?.messages]);

  useEffect(() => {
    if (!currentConversation) {
      createNewConversation();
    }
  }, [currentConversation, createNewConversation]);

  useEffect(() => {
    if (currentAssistantMessageId && assistantMessageContent !== '') {
      updateMessage(currentConversation?.id || '', currentAssistantMessageId, {
        content: assistantMessageContent,
        isLoading: false
      });
    }
  }, [assistantMessageContent, currentAssistantMessageId, currentConversation?.id]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !currentConversation) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isLoading: true,
    };

    console.log('Sending message:', {
      content: userMessage.content,
      threadId: currentConversation.threadId,
      selectedKbId,
      conversationId: currentConversation.id
    });

    addMessage(currentConversation.id, userMessage);
    addMessage(currentConversation.id, assistantMessage);
    
    setInputValue('');
    setIsLoading(true);
    setAssistantMessageContent(''); 
    setCurrentAssistantMessageId(assistantMessage.id);

    try {
      await streamChat(
        userMessage.content,
        (chunk: ChatResponse) => {
          console.log('Received chunk:', chunk);
          console.log('Chunk type:', chunk.type);
          console.log('Chunk content:', chunk.content);
          
          setAssistantMessageContent(prevContent => {
            let newContent = prevContent;
            console.log('Previous content:', prevContent);
            
            if (chunk.type === 'thinking') {
              newContent = prevContent + (prevContent ? '\n\n' : '') + chunk.content;
            } else if (chunk.type === 'tool_result' || chunk.type === 'kb_info') {
              newContent = prevContent + (prevContent ? '\n\n' : '') + chunk.content;
            }
            
            console.log('New content:', newContent);
            return newContent;
          });
        },
        selectedKbId, 
        currentConversation.threadId, 
        (error: string) => {
          console.error('API Error:', error);
          setAssistantMessageContent(`Sorry, an error occurred: ${error}`);
        }
      );
    } catch (error) {
      console.error('Chat error:', error);
      setAssistantMessageContent('Sorry, an error occurred while connecting to the server. Please check your network connection or try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!currentConversation) {
    return (
      <div className="flex flex-col h-full bg-white dark:bg-gray-900">
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Header toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleLeftSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">AI Assistant</h1>
        </div>
        <div className="flex items-center gap-2">
          {selectedKbId && (
            <div className="px-2 py-1 text-xs bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded">
              Knowledge base enabled
            </div>
          )}
          <button
            onClick={createNewConversation}
            className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-1"
          >
            <Plus className="w-3 h-3" />
            New chat
          </button>
        </div>
      </div>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {currentConversation.messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            
            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
              }`}
            >
              {message.isLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Thinking...</span>
                </div>
              ) : (
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              )}
            </div>

            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your question..."
            className="flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
} 