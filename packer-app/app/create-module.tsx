import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { useAuthStore } from '@/stores/useAuthStore';
import { usePackingStore } from '@/stores/usePackingStore';
import { ItemRow } from '@/components/ItemRow';
import { AddItemForm } from '@/components/AddItemForm';
import { theme } from '@/constants/theme';

export default function CreateModuleScreen() {
  const user = useAuthStore((s) => s.user);
  const modules = usePackingStore((s) => s.modules);
  const createModule = usePackingStore((s) => s.createModule);

  const [name, setName] = useState('');
  const [items, setItems] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);

  const addItem = (item: string) => {
    if (items.includes(item)) {
      Alert.alert('Duplicate', 'This item already exists.');
      return;
    }
    setItems((prev) => [...prev, item]);
  };

  const removeItem = (item: string) => {
    setItems((prev) => prev.filter((i) => i !== item));
  };

  const handleCreate = async () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter a module name.');
      return;
    }
    if (modules.some((m) => m.name.toLowerCase() === name.trim().toLowerCase())) {
      Alert.alert('Error', `A module named "${name.trim()}" already exists.`);
      return;
    }
    if (!user) return;
    setSaving(true);
    try {
      const id = await createModule(user.uid, name.trim(), items);
      router.replace(`/module/${id}`);
    } catch (e: any) {
      Alert.alert('Error', e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.label}>Module name</Text>
      <TextInput
        style={styles.input}
        value={name}
        onChangeText={setName}
        placeholder="e.g. Beach day"
        placeholderTextColor={theme.colors.textMuted}
      />

      <Text style={styles.sectionTitle}>Items</Text>
      <View style={styles.card}>
        {items.map((item) => (
          <ItemRow key={item} label={item} onDelete={() => removeItem(item)} />
        ))}
        {items.length === 0 && (
          <Text style={styles.emptyItems}>No items added yet.</Text>
        )}
        <AddItemForm placeholder="Add item" onAdd={addItem} />
      </View>

      <TouchableOpacity
        style={[styles.createBtn, saving && styles.createBtnDisabled]}
        onPress={handleCreate}
        disabled={saving}
      >
        <Text style={styles.createBtnText}>
          {saving ? 'Creating...' : 'Create module'}
        </Text>
      </TouchableOpacity>
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
  label: {
    fontSize: theme.fontSize.md,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  input: {
    backgroundColor: theme.colors.inputBackground,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
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
  createBtn: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginTop: theme.spacing.xl,
  },
  createBtnDisabled: {
    opacity: 0.6,
  },
  createBtnText: {
    color: theme.colors.white,
    fontSize: theme.fontSize.lg,
    fontWeight: '600',
  },
});
