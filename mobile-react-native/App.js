import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  StatusBar as NativeStatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

import Composer from './src/components/Composer';
import MessageBubble from './src/components/MessageBubble';
import {
  checkBackendHealth,
  getResolvedApiBaseUrl,
  resetChatSession,
  sendChatMessage,
} from './src/services/chatApi';

const QUICK_PROMPTS = [
  'Estou com palpitação',
  'Minha pressão está alta',
  'O que é ecocardiograma?',
  'Como me preparo para a consulta?',
];

const INITIAL_MESSAGE = {
  id: 'assistant-initial',
  role: 'assistant',
  text:
    'Olá! Sou o CardioIA Conversacional. Posso orientar sobre sintomas, pressão arterial, exames cardíacos e preparo para consulta. Em caso de sinais de urgência, procure atendimento imediato.',
  urgencyLevel: 'baixa',
};

function createMessage(role, text, extra = {}) {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    role,
    text,
    ...extra,
  };
}

export default function App() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Verificando backend...');
  const [connectionTone, setConnectionTone] = useState('neutral');
  const listRef = useRef(null);
  const apiBaseUrl = useMemo(() => getResolvedApiBaseUrl(), []);

  useEffect(() => {
    async function loadHealth() {
      try {
        const result = await checkBackendHealth();
        const mode = result.watson_configured ? 'Watson ativo' : 'Modo local ativo';
        setConnectionStatus(`Backend online • ${mode}`);
        setConnectionTone('success');
      } catch (error) {
        setConnectionStatus(`Backend indisponível • ${error.message}`);
        setConnectionTone('danger');
      }
    }

    loadHealth();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      listRef.current?.scrollToEnd?.({ animated: true });
    }, 80);

    return () => clearTimeout(timer);
  }, [messages]);

  async function handleSend(textOverride) {
    const content = String(textOverride ?? inputValue).trim();
    if (!content || isSending) return;

    const userMessage = createMessage('user', content);
    setMessages((current) => [...current, userMessage]);
    setInputValue('');
    setIsSending(true);

    try {
      const result = await sendChatMessage(content);
      const assistantMessage = createMessage('assistant', result.response, {
        urgencyLevel: result.urgency_level,
        source: result.source,
        topIntent: result.top_intent,
      });
      setMessages((current) => [...current, assistantMessage]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        createMessage(
          'assistant',
          `Não foi possível consultar o assistente agora. Detalhe: ${error.message}`,
          { urgencyLevel: 'baixa' }
        ),
      ]);
    } finally {
      setIsSending(false);
    }
  }

  async function handleReset() {
    if (isResetting) return;

    setIsResetting(true);
    try {
      await resetChatSession();
      setMessages([INITIAL_MESSAGE]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        createMessage('assistant', `Não foi possível reiniciar a sessão. Detalhe: ${error.message}`),
      ]);
    } finally {
      setIsResetting(false);
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 8 : 0}
      >
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.title}>Assistente Cardiológico</Text>
              <Text style={styles.subtitle}>Interface React Native integrada ao backend Flask</Text>
            </View>
            <Pressable
              style={[styles.resetButton, isResetting && styles.resetButtonDisabled]}
              onPress={handleReset}
              disabled={isResetting}
            >
              <Text style={styles.resetButtonText}>{isResetting ? '...' : 'Reiniciar'}</Text>
            </Pressable>
          </View>

          <View style={styles.connectionBox}>
            <View
              style={[
                styles.connectionIndicator,
                connectionTone === 'success'
                  ? styles.connectionSuccess
                  : connectionTone === 'danger'
                  ? styles.connectionDanger
                  : styles.connectionNeutral,
              ]}
            />
            <View style={styles.connectionTextWrap}>
              <Text style={styles.connectionTitle}>{connectionStatus}</Text>
              <Text style={styles.connectionUrl}>API: {apiBaseUrl}</Text>
            </View>
          </View>

          <Text style={styles.disclaimer}>
            Protótipo educacional. Não realiza diagnóstico e não substitui avaliação médica.
          </Text>
        </View>

        <View style={styles.quickPromptRow}>
          <FlatList
            horizontal
            data={QUICK_PROMPTS}
            keyExtractor={(item) => item}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.quickPromptList}
            renderItem={({ item }) => (
              <Pressable style={styles.quickPromptChip} onPress={() => handleSend(item)}>
                <Text style={styles.quickPromptText}>{item}</Text>
              </Pressable>
            )}
          />
        </View>

        <FlatList
          ref={listRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => <MessageBubble item={item} />}
          contentContainerStyle={styles.chatList}
          keyboardShouldPersistTaps="handled"
          ListFooterComponent={
            isSending ? (
              <View style={styles.loadingRow}>
                <ActivityIndicator size="small" color="#dc2626" />
                <Text style={styles.loadingText}>Assistente respondendo...</Text>
              </View>
            ) : (
              <View style={styles.chatBottomSpace} />
            )
          }
        />

        <Composer
          value={inputValue}
          onChangeText={setInputValue}
          onSend={() => handleSend()}
          disabled={isSending || isResetting}
        />
      </KeyboardAvoidingView>
      {Platform.OS === 'android' ? <View style={{ height: NativeStatusBar.currentHeight || 0 }} /> : null}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#eef4fb',
  },
  container: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 18,
    paddingTop: 18,
    paddingBottom: 10,
    backgroundColor: '#eef4fb',
  },
  headerTop: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0f172a',
  },
  subtitle: {
    marginTop: 6,
    fontSize: 13,
    color: '#475569',
  },
  resetButton: {
    backgroundColor: '#0f172a',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 14,
  },
  resetButtonDisabled: {
    opacity: 0.6,
  },
  resetButtonText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 13,
  },
  connectionBox: {
    marginTop: 14,
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: '#dbe4f0',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  connectionIndicator: {
    width: 12,
    height: 12,
    borderRadius: 999,
  },
  connectionSuccess: {
    backgroundColor: '#16a34a',
  },
  connectionDanger: {
    backgroundColor: '#dc2626',
  },
  connectionNeutral: {
    backgroundColor: '#f59e0b',
  },
  connectionTextWrap: {
    flex: 1,
  },
  connectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
  },
  connectionUrl: {
    marginTop: 4,
    fontSize: 12,
    color: '#64748b',
  },
  disclaimer: {
    marginTop: 12,
    fontSize: 12,
    color: '#64748b',
  },
  quickPromptRow: {
    paddingTop: 6,
    paddingBottom: 8,
  },
  quickPromptList: {
    paddingHorizontal: 18,
    gap: 10,
  },
  quickPromptChip: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  quickPromptText: {
    fontSize: 13,
    color: '#1e293b',
    fontWeight: '600',
  },
  chatList: {
    paddingHorizontal: 18,
    paddingTop: 6,
    paddingBottom: 12,
  },
  loadingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 14,
  },
  loadingText: {
    fontSize: 13,
    color: '#64748b',
  },
  chatBottomSpace: {
    height: 10,
  },
});
