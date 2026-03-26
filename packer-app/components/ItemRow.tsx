import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { theme } from '@/constants/theme';

interface ItemRowProps {
  label: string;
  checked?: boolean;
  onToggle?: () => void;
  onDelete?: () => void;
}

export function ItemRow({ label, checked, onToggle, onDelete }: ItemRowProps) {
  return (
    <View style={styles.row}>
      <TouchableOpacity
        style={styles.labelContainer}
        onPress={onToggle}
        disabled={!onToggle}
      >
        {onToggle && (
          <View style={[styles.checkbox, checked && styles.checkboxChecked]}>
            {checked && <Text style={styles.checkmark}>✓</Text>}
          </View>
        )}
        <Text style={[styles.label, checked && styles.labelChecked]}>{label}</Text>
      </TouchableOpacity>
      {onDelete && (
        <TouchableOpacity onPress={onDelete} style={styles.deleteBtn}>
          <Text style={styles.deleteText}>🗑</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    backgroundColor: theme.colors.cardBackground,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  labelContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: theme.colors.primary,
    marginRight: theme.spacing.sm,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: theme.colors.primary,
  },
  checkmark: {
    color: theme.colors.white,
    fontSize: 14,
    fontWeight: 'bold',
  },
  label: {
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
    flex: 1,
  },
  labelChecked: {
    color: theme.colors.textMuted,
    textDecorationLine: 'line-through',
  },
  deleteBtn: {
    padding: theme.spacing.xs,
  },
  deleteText: {
    fontSize: 18,
  },
});
