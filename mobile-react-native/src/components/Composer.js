import React from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

export default function Composer({ value, onChangeText, onSend, disabled }) {
  const canSend = value.trim().length > 0 && !disabled;

  return (
    <View style={styles.wrapper}>
      <TextInput
        style={styles.input}
        placeholder="Digite sua mensagem"
        placeholderTextColor="#64748b"
        multiline
        value={value}
        onChangeText={onChangeText}
        editable={!disabled}
      />
      <Pressable
        style={[styles.button, !canSend && styles.buttonDisabled]}
        onPress={onSend}
        disabled={!canSend}
      >
        <Text style={styles.buttonText}>Enviar</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#dbe4f0',
    paddingHorizontal: 12,
    paddingVertical: 12,
    gap: 10,
  },
  input: {
    flex: 1,
    minHeight: 48,
    maxHeight: 110,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: '#0f172a',
    backgroundColor: '#f8fafc',
  },
  button: {
    minHeight: 48,
    paddingHorizontal: 18,
    borderRadius: 16,
    backgroundColor: '#dc2626',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 15,
  },
});
