# CardioIA Conversacional Mobile

Aplicação básica em React Native com Expo para interação com o backend Flask da Fase 5.

## Requisitos
- Node.js compatível com o SDK do Expo utilizado
- Backend Flask da pasta raiz em execução

## Configuração
1. Copie `.env.example` para `.env`.
2. Ajuste `EXPO_PUBLIC_API_URL`:
   - em emulador Android local, pode usar `http://10.0.2.2:5000`
   - em iOS Simulator, `http://127.0.0.1:5000`
   - em dispositivo físico, use o IP da sua máquina na rede local, por exemplo `http://192.168.0.10:5000`

## Execução
```bash
npm install
npx expo start
```

## Funcionalidades
- envio de mensagens ao endpoint `/api/chat`
- exibição das respostas do assistente
- reinício da sessão com `/api/reset`
- verificação simples de disponibilidade com `/api/health`
- mensagens iniciais de exemplo para facilitar a demonstração acadêmica

## Observação
Este protótipo é educacional e não substitui avaliação médica.
