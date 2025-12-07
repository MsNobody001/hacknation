import axios from 'axios';
import { SendChatMsgResponse } from '@/types';

export const chatService = {
  send_chat_msg: async (msg: string) => {
    const response = await axios.post<SendChatMsgResponse>('https://webapp-user-assistant-ejhpgseje3f5c7ft.swedencentral-01.azurewebsites.net/accident-data-collector/', {
      input: msg,
      session_id: localStorage.getItem('sessionId'),
    })
    return response.data;
  },
};
