import { apiRequest } from './apiClient';

export async function sendChatMessage({ message, history = [], userId = null }) {
  return apiRequest('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      history,
      user_id: userId,
      source_lang: 'en_XX',
      target_lang: 'en_XX'
    })
  });
}
