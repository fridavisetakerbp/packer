import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, Alert } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { useAuthStore } from '@/stores/useAuthStore';
import { usePackingStore } from '@/stores/usePackingStore';
import { ItemRow } from '@/components/ItemRow';
import { AddItemForm } from '@/components/AddItemForm';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { theme } from '@/constants/theme';

export default function ModuleDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const user = useAuthStore((s) => s.user);
  const modules = usePackingStore((s) => s.modules);
  const updateModule = usePackingStore((s) => s.updateModule);
  const deleteModule = usePackingStore((s) => s.deleteModule);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const mod = modules.find((m) => m.id === id);

  if (!mod || !user) {
    return (
      <View style={styles.container}>
        <Text style={styles.emptyText}>Module not found.</Text>
      </View>
    );
  }

  const addItem = (item: string) => {
    if (mod.items.includes(item)) {
      Alert.alert('Duplicate', 'This item already exists in the module.');
      return;
    }
    updateModule(user.uid, mod.id, { items: [...mod.items, item] });
  };

  const removeItem = (item: string) => {
    updateModule(user.uid, mod.id, {
      items: mod.items.filter((i) => i !== item),
    });
  };

  const handleDelete = async () => {
    await deleteModule(user.uid, mod.id);
    router.back();
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{mod.name}</Text>

      <Text style={styles.sectionTitle}>Items</Text>
      <View style={styles.card}>
        {mod.items.map((item) => (
          <ItemRow
            key={item}
            label={item}
            onDelete={() => removeItem(item)}
          />
        ))}
        {mod.items.length === 0 && (
          <Text style={styles.emptyItems}>No items yet.</Text>
        )}
        <AddItemForm placeholder="Add item" onAdd={addItem} />
      </View>

      <Text
        style={styles.deleteBtn}
        onPress={() => setConfirmDelete(true)}
      >
        Delete this module
      </Text>

      <ConfirmDialog
        visible={confirmDelete}
        message={`Are you sure you want to delete "${mod.name}"?`}
        onConfirm={handleDelete}
        onCancel={() => setConfirmDelete(false)}
      />
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
  title: {
    fontSize: theme.fontSize.xl,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
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
  emptyItems: {
    padding: theme.spacing.md,
    textAlign: 'center',
    color: theme.colors.textSecondary,
    fontSize: theme.fontSize.md,
  },
  emptyText: {
    padding: theme.spacing.lg,
    textAlign: 'center',
    color: theme.colors.textSecondary,
    fontSize: theme.fontSize.md,
  },
  deleteBtn: {
    color: theme.colors.danger,
    fontSize: theme.fontSize.md,
    textAlign: 'center',
    marginTop: theme.spacing.xl,
    padding: theme.spacing.md,
  },
});
