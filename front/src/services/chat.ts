import axios from 'axios';

export interface SendChatMsgResponse {
  response: string;
  session_id: string;
  collected_data: {
    accident_date: string | null,
    accident_time: string | null,
    location: string | null,
    work_start_time: string | null,
    work_end_time: string | null,
    injury_type: string | null,
    circumstances: string | null,
    cause: string | null,
    place_description: string | null,
    medical_help: string | null,
    investigation: string | null,
    machines_involved: string | null,
    machine_condition: string | null,
    proper_use: string | null,
    machine_description: string | null,
    machine_certification: string | null,
    machine_registry: string | null,
    witnesses: string | null,
    activity_before_accident: string | null,
    event_sequence: string | null,
    direct_cause: string | null,
    indirect_causes: string | null
  }
}

export const chatService = {
  send_chat_msg: async (msg: string) => {
    const response = await axios.post<SendChatMsgResponse>('https://webapp-user-assistant-ejhpgseje3f5c7ft.swedencentral-01.azurewebsites.net/accident-data-collector/', {
      input: msg,
    })
    return response.data;
  },
};
