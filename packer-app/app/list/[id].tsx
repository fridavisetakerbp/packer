import React, { useState } from 'react';
import { View, Text, ScrollView, StyleSheet, Alert } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { useAuthStore } from '@/stores/useAuthStore';
import { usePackingStore } from '@/stores/usePackingStore';
import { ItemRow } from '@/components/ItemRow';
import { AddItemForm } from '@/components/AddItemForm';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { theme } from '@/constants/theme';

export default function ListDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const user = useAuthStore((s) => s.user);
  const lists = usePackingStore((s) => s.lists);
  const updateList = usePackingStore((s) => s.updateList);
  const deleteList = usePackingStore((s) => s.deleteList);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const list = lists.find((l) => l.id === id);

  if (!list || !user) {
    return (
      <View style={styles.container}>
        <Text style={styles.emptyText}>List not found.</Text>
      </View>
    );
  }

  const toPack = Object.entries(list.items).filter(([, packed]) => !packed);
  const packed = Object.entries(list.items).filter(([, packed]) => packed);

  const toggleItem = (item: string) => {
    const newItems = { ...list.items, [item]: !list.items[item] };
    updateList(user.uid, list.id, { items: newItems });
  };

  const deleteItem = (item: string) => {
    const newItems = { ...list.items };
    delete newItems[item];
    updateList(user.uid, list.id, { items: newItems });
  };

  const addItem = (item: string) => {
    if (list.items.hasOwnProperty(item)) {
      Alert.alert('Duplicate', 'This item is already in the list.');
      return;
    }
    updateList(user.uid, list.id, { items: { ...list.items, [item]: false } });
  };

  const handleDelete = async () => {
    await deleteList(user.uid, list.id);
    router.back();
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{list.name}</Text>

      <Text style={styles.sectionTitle}>
        To pack ({toPack.length})
      </Text>
      <View style={styles.card}>
        {toPack.map(([item]) => (
          <ItemRow
            key={item}
            label={item}
            checked={false}
            onToggle={() => toggleItem(item)}
            onDelete={() => deleteItem(item)}
          />
        ))}
        {toPack.length === 0 && (
          <Text style={styles.allPacked}>All packed! 🎉</Text>
        )}
      </View>

      {packed.length > 0 && (
        <>
          <Text style={styles.sectionTitle}>
            Packed ({packed.length})
          </Text>
          <View style={styles.card}>
            {packed.map(([item]) => (
              <ItemRow
                key={item}
                label={item}
                checked={true}
                onToggle={() => toggleItem(item)}
                onDelete={() => deleteItem(item)}
              />
            ))}
          </View>
        </>
      )}

      <Text style={styles.sectionTitle}>Add custom item</Text>
      <View style={styles.card}>
        <AddItemForm placeholder="Add item" onAdd={addItem} />
      </View>

      <Text
        style={styles.deleteBtn}
        onPress={() => setConfirmDelete(true)}
      >
        Delete this list
      </Text>

      <ConfirmDialog
        visible={confirmDelete}
        message="Are you sure you want to delete this packing list?"
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
  allPacked: {
    padding: theme.spacing.md,
    textAlign: 'center',
    fontSize: theme.fontSize.md,
    color: theme.colors.success,
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
