'use client';

import { useState } from 'react';
import LeftSidebar from './LeftSidebar';
import ChatInterface from './ChatInterface';

export default function ChatLayout() {
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-gray-900">
      {/* 左侧边栏 */}
      <LeftSidebar 
        isOpen={leftSidebarOpen} 
        onToggle={() => setLeftSidebarOpen(!leftSidebarOpen)} 
      />
      
      {/* 主聊天区域 */}
      <div className="flex-1 flex flex-col">
        <ChatInterface 
          onToggleLeftSidebar={() => setLeftSidebarOpen(!leftSidebarOpen)}
        />
      </div>
    </div>
  );
} 