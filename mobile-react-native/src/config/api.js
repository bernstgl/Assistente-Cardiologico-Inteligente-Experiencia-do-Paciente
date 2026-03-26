import { Platform } from 'react-native';

function normalizeBaseUrl(value) {
  return String(value || '').trim().replace(/\/$/, '');
}

export function getApiBaseUrl() {
  const fromEnv = normalizeBaseUrl(process.env.EXPO_PUBLIC_API_URL);

  if (fromEnv) {
    return fromEnv;
  }

  if (Platform.OS === 'android') {
    return 'http://10.0.2.2:5000';
  }

  return 'http://127.0.0.1:5000';
}
