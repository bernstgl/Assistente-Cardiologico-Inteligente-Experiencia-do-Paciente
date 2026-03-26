import { getApiBaseUrl } from '../config/api';

const API_BASE_URL = getApiBaseUrl();

async function handleResponse(response) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data?.error || 'Falha ao comunicar com o backend.';
    throw new Error(message);
  }

  return data;
}

export function getResolvedApiBaseUrl() {
  return API_BASE_URL;
}

export async function sendChatMessage(message) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  return handleResponse(response);
}

export async function resetChatSession() {
  const response = await fetch(`${API_BASE_URL}/api/reset`, {
    method: 'POST',
  });

  return handleResponse(response);
}

export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  return handleResponse(response);
}
