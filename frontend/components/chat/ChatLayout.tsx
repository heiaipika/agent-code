'use client';

import { useState } from 'react';
import LeftSidebar from './LeftSidebar';
import ChatInterface from './ChatInterface';
import { ChatProvider } from '@/lib/contexts/ChatContext';

export default function ChatLayout() {
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);

  return (
    <ChatProvider>
      <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
        {/* left sidebar */}
        <LeftSidebar 
          isOpen={leftSidebarOpen} 
          onToggle={() => setLeftSidebarOpen(!leftSidebarOpen)} 
        />
        
        {/* chat main area */}
        <div className="flex-1 flex flex-col">
          <ChatInterface 
            onToggleLeftSidebar={() => setLeftSidebarOpen(!leftSidebarOpen)}
          />
        </div>
      </div>
    </ChatProvider>
  );
} 