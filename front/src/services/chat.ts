import axios from 'axios';
import { SendChatMsgResponse } from '@/types';

export const chatService = {
  send_chat_report: async (msg: string) => {
    const response = await axios.post<SendChatMsgResponse>('https://webapp-user-assistant-ejhpgseje3f5c7ft.swedencentral-01.azurewebsites.net/accident-report-collector/', {
      input: msg,
      session_id: localStorage.getItem('sessionId'),
    })
    return response.data;
  },

  send_chat_statement: async (msg: string) => {
    const response = await axios.post<SendChatMsgResponse>('https://webapp-user-assistant-ejhpgseje3f5c7ft.swedencentral-01.azurewebsites.net/accident-statement-collector/', {
      input: msg,
      session_id: localStorage.getItem('sessionId'),
    })
    return response.data;
  },
};

