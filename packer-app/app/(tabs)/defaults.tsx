import React from 'react';
import { View, Text, ScrollView, StyleSheet, Alert } from 'react-native';
import { useAuthStore } from '@/stores/useAuthStore';
import { usePackingStore } from '@/stores/usePackingStore';
import { ItemRow } from '@/components/ItemRow';
import { AddItemForm } from '@/components/AddItemForm';
import { theme } from '@/constants/theme';

export default function DefaultsScreen() {
  const user = useAuthStore((s) => s.user);
  const defaults = usePackingStore((s) => s.defaults);
  const updateDefaults = usePackingStore((s) => s.updateDefaults);

  if (!user) return null;

  const addItem = (key: 'daily' | 'base' | 'base_sleepover', item: string) => {
    if (defaults[key].includes(item)) {
      Alert.alert('Duplicate', 'This item already exists.');
      return;
    }
    updateDefaults(user.uid, {
      ...defaults,
      [key]: [...defaults[key], item],
    });
  };

  const removeItem = (key: 'daily' | 'base' | 'base_sleepover', item: string) => {
    updateDefaults(user.uid, {
      ...defaults,
      [key]: defaults[key].filter((i) => i !== item),
    });
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.sectionTitle}>Nightly items (scaled with nights)</Text>
      <View style={styles.card}>
        {defaults.daily.map((item) => (
          <ItemRow
            key={item}
            label={item}
            onDelete={() => removeItem('daily', item)}
          />
        ))}
        <AddItemForm
          placeholder="Add nightly item"
          buttonLabel="Add"
          onAdd={(item) => addItem('daily', item)}
        />
      </View>

      <Text style={styles.sectionTitle}>Base items (always included)</Text>
      <View style={styles.card}>
        {defaults.base.map((item) => (
          <ItemRow
            key={item}
            label={item}
            onDelete={() => removeItem('base', item)}
          />
        ))}
        <AddItemForm
          placeholder="Add base item"
          buttonLabel="Add"
          onAdd={(item) => addItem('base', item)}
        />
      </View>

      <Text style={styles.sectionTitle}>Sleepover items (only when sleeping over)</Text>
      <View style={styles.card}>
        {defaults.base_sleepover.map((item) => (
          <ItemRow
            key={item}
            label={item}
            onDelete={() => removeItem('base_sleepover', item)}
          />
        ))}
        <AddItemForm
          placeholder="Add sleepover item"
          buttonLabel="Add"
          onAdd={(item) => addItem('base_sleepover', item)}
        />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: theme.spacing.md,
    paddingBottom: 100,
  },
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: '600',
    color: theme.colors.text,
    marginTop: theme.spacing.lg,
    marginBottom: theme.spacing.sm,
  },
  card: {
    backgroundColor: theme.colors.cardBackground,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
});
