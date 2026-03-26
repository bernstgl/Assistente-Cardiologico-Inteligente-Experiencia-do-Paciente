import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

function getUrgencyStyle(level) {
  if (level === 'alta') return styles.urgencyHigh;
  if (level === 'moderada') return styles.urgencyModerate;
  return styles.urgencyLow;
}

function getUrgencyLabel(level) {
  if (level === 'alta') return 'Urgência alta';
  if (level === 'moderada') return 'Urgência moderada';
  return 'Urgência baixa';
}

export default function MessageBubble({ item }) {
  const isUser = item.role === 'user';
  const bubbleStyle = isUser ? styles.userBubble : styles.assistantBubble;
  const containerStyle = isUser ? styles.userRow : styles.assistantRow;
  const textStyle = isUser ? styles.userText : styles.assistantText;

  return (
    <View style={[styles.row, containerStyle]}>
      <View style={[styles.bubble, bubbleStyle]}>
        {!isUser ? <Text style={styles.sender}>Assistente</Text> : null}
        <Text style={[styles.messageText, textStyle]}>{item.text}</Text>
        {!isUser && item.urgencyLevel ? (
          <View style={[styles.urgencyChip, getUrgencyStyle(item.urgencyLevel)]}>
            <Text style={styles.urgencyChipText}>{getUrgencyLabel(item.urgencyLevel)}</Text>
          </View>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    marginBottom: 12,
    flexDirection: 'row',
  },
  assistantRow: {
    justifyContent: 'flex-start',
  },
  userRow: {
    justifyContent: 'flex-end',
  },
  bubble: {
    maxWidth: '85%',
    borderRadius: 18,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  assistantBubble: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#dbe4f0',
  },
  userBubble: {
    backgroundColor: '#1d4ed8',
  },
  sender: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 6,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  assistantText: {
    color: '#0f172a',
  },
  userText: {
    color: '#ffffff',
  },
  urgencyChip: {
    alignSelf: 'flex-start',
    marginTop: 10,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
  },
  urgencyHigh: {
    backgroundColor: '#fee2e2',
  },
  urgencyModerate: {
    backgroundColor: '#fef3c7',
  },
  urgencyLow: {
    backgroundColor: '#dcfce7',
  },
  urgencyChipText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
});
