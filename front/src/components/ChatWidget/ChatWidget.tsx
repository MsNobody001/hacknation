import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot } from 'lucide-react';
import { CollectedData, Message } from '@/types';
import { chatService,  } from '@/services/chat';

export interface ChatWidgetProps {
  initialMessages?: Message[];
  title?: string;
  subtitle?: string;
  agentAvatar?: string;
  onCollectedData?: (data: CollectedData) => void;
}

const MAX_HEIGHT_PX = 150;

export const ChatWidget: React.FC<ChatWidgetProps> = ({ initialMessages = [], onCollectedData }) => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>(initialMessages.reverse());
  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const pushMessage = useCallback((text: string, sender: 'user' | 'agent') => {
    setMessages(prevMessages => [
      ...prevMessages,
      {
        id: crypto.randomUUID(),
        text: text,
        sender,
      },
    ]);
  }, []);

  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, MAX_HEIGHT_PX);
      textarea.style.height = `${newHeight}px`;
      if (textarea.scrollHeight > MAX_HEIGHT_PX) {
        textarea.classList.add('overflow-y-auto');
      } else {
        textarea.classList.remove('overflow-y-auto');
      }
    }
  }, []);

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue, adjustTextareaHeight]);

  const handleSendMessage = (e?: React.FormEvent) => {
    e?.preventDefault();

    if (!inputValue.trim()) return;

    pushMessage(inputValue, 'user');

    setIsTyping(true);

    chatService
      .send_chat_msg(inputValue)
      .then(response => {
        pushMessage(response.response, 'agent');
        if (onCollectedData) onCollectedData(response.collected_data);
        setIsTyping(true);
      })
      .catch(() => {
        void 0;
      })
      .finally(() => {
        setIsTyping(false);
      });

    setInputValue('');

    // Reset textarea height to 1 row after sending
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.classList.remove('overflow-y-auto');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div
      className={`
        origin-bottom-right transition-all duration-300 ease-out
        scale-100 opacity-100 translate-y-0
        bg-white flex flex-col overflow-hidden h-full
      `}
    >
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto  bg-slate-50 flex flex-col justify-end">
        <div className="h-full p-4 space-y-6 flex flex-col">
        {/* Date Separator Example */}
        {/* <div className="flex justify-center">
          <span className="text-xs font-medium text-slate-400 bg-slate-200/50 px-3 py-1 rounded-full">Today</span>
        </div> */}

        {messages.length === 0 && (
          <div className="flex justify-center my-4">
            <span className="text-xs text-center text-slate-500 italic">
              Cześć! Jestem tutaj, aby pomóc Ci wypełnić formularz wyjaśnienia wypadku. Proszę, opowiedz mi, co się
              stało.
            </span>
          </div>
        )}

        {messages.map(msg => {
          const isUser = msg.sender === 'user';
          return (
            <div key={msg.id} className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end gap-2`}>
                {!isUser && (
                  <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                    <Bot size={14} />
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={`
                    group relative px-4 py-2.5 rounded-2xl shadow-sm text-sm leading-relaxed
                    ${
                      isUser
                        ? `bg-primary text-white rounded-br-sm`
                        : 'bg-white  text-slate-700 border border-slate-200  rounded-bl-sm'
                    }
                  `}
                >
                  {msg.text}
                  {/* <div className={`
                    text-[10px] mt-1 opacity-70
                    ${isUser ? 'text-indigo-100 text-right' : 'text-slate-400 text-left'}
                  `}>
                    {formatTime(msg.timestamp)}
                  </div> */}
                </div>
              </div>
            </div>
          );
        })}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex w-full justify-start">
            <div className="flex items-end gap-2">
              <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center flex-shrink-0">
                <Bot size={14} />
              </div>
              <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Invisible div to scroll to */}
        <div ref={messagesEndRef}
        className="pt-1" />
        </div>

      </div>

      {/* Input Area */}
      <div className="p-3 bg-white border-t border-slate-200">
        <form
          onSubmit={handleSendMessage}
          className="flex items-end gap-2 bg-slate-100 p-2 rounded-xl border border-transparent transition-all"
        >
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-slate-700  placeholder:text-slate-400 resize-none"
            rows={1}
            style={{ maxHeight: `${MAX_HEIGHT_PX}px`, padding: '8px 0' }}
          />

          <button
            type="submit"
            disabled={!inputValue.trim()}
            className={`
              p-2 rounded-lg transition-all duration-200
              ${
                inputValue.trim()
                  ? 'bg-green-100 text-white shadow-md hover:bg-green-200 transform hover:scale-105'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }
            `}
          >
            <Send color="green" size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};
