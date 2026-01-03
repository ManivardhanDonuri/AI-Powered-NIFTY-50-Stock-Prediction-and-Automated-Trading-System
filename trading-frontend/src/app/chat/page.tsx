'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, History, Settings, Plus, Trash2 } from 'lucide-react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import AITradingChatInterface from '@/components/chat/AITradingChatInterface';
import { Conversation } from '@/types/chat';

const ChatPage: React.FC = () => {
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showSidebar, setShowSidebar] = useState(true);
  const [loading, setLoading] = useState(false);
  
  // Load conversation history
  useEffect(() => {
    loadConversations();
  }, []);
  
  const loadConversations = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/chat/conversations');
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations.map((conv: any) => ({
          id: conv.id,
          createdAt: new Date(conv.created_at),
          updatedAt: new Date(conv.updated_at),
          messageCount: conv.message_count,
          lastMessage: conv.last_message ? {
            content: conv.last_message.content,
            timestamp: new Date(conv.last_message.timestamp),
            type: conv.last_message.message_type
          } : undefined
        })));
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleNewConversation = () => {
    setCurrentConversationId(undefined);
  };
  
  const handleConversationSelect = (conversationId: string) => {
    setCurrentConversationId(conversationId);
  };
  
  const handleConversationChange = (conversationId: string) => {
    setCurrentConversationId(conversationId);
    loadConversations(); // Refresh conversation list
  };
  
  const handleDeleteConversation = async (conversationId: string) => {
    if (!confirm('Are you sure you want to delete this conversation?')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/v1/chat/conversation/${conversationId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));
        
        // If we're deleting the current conversation, start a new one
        if (currentConversationId === conversationId) {
          setCurrentConversationId(undefined);
        }
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };
  
  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };
  
  return (
    <DashboardLayout>
      <div className="flex h-full">
        {/* Sidebar */}
        <motion.div
          initial={false}
          animate={{ width: showSidebar ? 320 : 0 }}
          transition={{ duration: 0.2 }}
          className="flex-shrink-0 overflow-hidden border-r border-gray-200 dark:border-gray-700"
        >
          <div className="w-80 h-full flex flex-col bg-gray-50 dark:bg-gray-800">
            {/* Sidebar Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Chat History
                </h2>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowSidebar(false)}
                  className="p-1"
                >
                  <History className="w-4 h-4" />
                </Button>
              </div>
              
              <Button
                onClick={handleNewConversation}
                className="w-full"
                size="sm"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Conversation
              </Button>
            </div>
            
            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto p-2">
              {loading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map(i => (
                    <div
                      key={i}
                      className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"
                    />
                  ))}
                </div>
              ) : conversations.length === 0 ? (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  <MessageCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No conversations yet</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {conversations.map((conversation) => (
                    <motion.div
                      key={conversation.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                        currentConversationId === conversation.id
                          ? 'bg-blue-100 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                      onClick={() => handleConversationSelect(conversation.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <MessageCircle className="w-3 h-3 text-gray-400" />
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {formatRelativeTime(conversation.updatedAt)}
                            </span>
                          </div>
                          
                          {conversation.lastMessage ? (
                            <p className="text-sm text-gray-900 dark:text-gray-100 line-clamp-2">
                              {conversation.lastMessage.content}
                            </p>
                          ) : (
                            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                              New conversation
                            </p>
                          )}
                          
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-400">
                              {conversation.messageCount} messages
                            </span>
                          </div>
                        </div>
                        
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteConversation(conversation.id);
                          }}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 h-6 w-6 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </motion.div>
        
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
            <div className="flex items-center gap-3">
              {!showSidebar && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowSidebar(true)}
                  className="p-2"
                >
                  <History className="w-4 h-4" />
                </Button>
              )}
              
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  AI Trading Assistant
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Get insights about your portfolio, market conditions, and trading signals
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
          
          {/* Chat Interface */}
          <div className="flex-1">
            <AITradingChatInterface
              conversationId={currentConversationId}
              contextType="trading"
              onNewConversation={handleConversationChange}
            />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ChatPage;