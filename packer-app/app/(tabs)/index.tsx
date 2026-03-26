import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { useAuthStore } from '@/stores/useAuthStore';
import { usePackingStore } from '@/stores/usePackingStore';
import { theme } from '@/constants/theme';
import { logout } from '@/services/auth';

export default function GenerateScreen() {
  const user = useAuthStore((s) => s.user);
  const modules = usePackingStore((s) => s.modules);
  const defaults = usePackingStore((s) => s.defaults);
  const createList = usePackingStore((s) => s.createList);

  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [nights, setNights] = useState('3');
  const [generatedItems, setGeneratedItems] = useState<Record<string, boolean> | null>(null);
  const [listName, setListName] = useState('');
  const [saving, setSaving] = useState(false);

  const toggleModule = (moduleId: string) => {
    setSelectedModules((prev) =>
      prev.includes(moduleId) ? prev.filter((id) => id !== moduleId) : [...prev, moduleId]
    );
  };

  const handleGenerate = () => {
    const nightsNum = parseInt(nights) || 0;
    const items = new Set<string>();

    for (const mod of modules) {
      if (selectedModules.includes(mod.id)) {
        mod.items.forEach((item) => items.add(item));
      }
    }

    if (nightsNum > 0) {
      defaults.base.forEach((item) => items.add(item));
      defaults.base_sleepover.forEach((item) => items.add(item));

      const clothing: Record<string, number> = {};
      for (const item of defaults.daily) {
        clothing[item] = nightsNum;
        items.delete(item);
      }

      const fullItems: Record<string, boolean> = {};
      for (const [k, v] of Object.entries(clothing)) {
        fullItems[`${k} x${v}`] = false;
      }
      for (const item of Array.from(items).sort()) {
        fullItems[item] = false;
      }
      setGeneratedItems(fullItems);
    } else {
      const fullItems: Record<string, boolean> = {};
      for (const item of Array.from(items).sort()) {
        fullItems[item] = false;
      }
      setGeneratedItems(fullItems);
    }
  };

  const handleSave = async () => {
    if (!listName.trim()) {
      Alert.alert('Error', 'Please enter a name for the list.');
      return;
    }
    if (!generatedItems || !user) return;
    setSaving(true);
    try {
      const id = await createList(user.uid, listName.trim(), generatedItems);
      setGeneratedItems(null);
      setListName('');
      setSelectedModules([]);
      router.push(`/list/${id}`);
    } catch (e: any) {
      Alert.alert('Error', e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.sectionTitle}>Select activities</Text>
      <View style={styles.moduleGrid}>
        {modules.map((mod) => (
          <TouchableOpacity
            key={mod.id}
            style={[
              styles.moduleChip,
              selectedModules.includes(mod.id) && styles.moduleChipSelected,
            ]}
            onPress={() => toggleModule(mod.id)}
          >
            <Text
              style={[
                styles.moduleChipText,
                selectedModules.includes(mod.id) && styles.moduleChipTextSelected,
              ]}
            >
              {mod.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.sectionTitle}>Nights</Text>
      <TextInput
        style={styles.nightsInput}
        value={nights}
        onChangeText={setNights}
        keyboardType="number-pad"
        placeholder="0"
      />

      <TouchableOpacity style={styles.generateBtn} onPress={handleGenerate}>
        <Text style={styles.generateBtnText}>Generate packing list</Text>
      </TouchableOpacity>

      {generatedItems && (
        <View style={styles.previewSection}>
          <Text style={styles.sectionTitle}>
            Preview ({Object.keys(generatedItems).length} items)
          </Text>
          {Object.keys(generatedItems).map((item) => (
            <View key={item} style={styles.previewItem}>
              <Text style={styles.previewItemText}>• {item}</Text>
            </View>
          ))}

          <View style={styles.saveSection}>
            <TextInput
              style={styles.saveInput}
              value={listName}
              onChangeText={setListName}
              placeholder="List name (e.g. Weekend trip)"
              placeholderTextColor={theme.colors.textMuted}
            />
            <TouchableOpacity
              style={[styles.saveBtn, saving && styles.saveBtnDisabled]}
              onPress={handleSave}
              disabled={saving}
            >
              <Text style={styles.saveBtnText}>
                {saving ? 'Saving...' : 'Save & open'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      <TouchableOpacity style={styles.logoutBtn} onPress={() => logout()}>
        <Text style={styles.logoutText}>Sign out</Text>
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
  sectionTitle: {
    fontSize: theme.fontSize.lg,
    fontWeight: '600',
    color: theme.colors.text,
    marginTop: theme.spacing.lg,
    marginBottom: theme.spacing.sm,
  },
  moduleGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  moduleChip: {
    backgroundColor: theme.colors.cardBackground,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.lg,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
  },
  moduleChipSelected: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  moduleChipText: {
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
  },
  moduleChipTextSelected: {
    color: theme.colors.white,
  },
  nightsInput: {
    backgroundColor: theme.colors.inputBackground,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.sm,
    fontSize: theme.fontSize.lg,
    color: theme.colors.text,
    width: 80,
    textAlign: 'center',
  },
  generateBtn: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginTop: theme.spacing.lg,
  },
  generateBtnText: {
    color: theme.colors.white,
    fontSize: theme.fontSize.lg,
    fontWeight: '600',
  },
  previewSection: {
    marginTop: theme.spacing.lg,
    backgroundColor: theme.colors.cardBackground,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
  },
  previewItem: {
    paddingVertical: 3,
  },
  previewItemText: {
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
  },
  saveSection: {
    marginTop: theme.spacing.lg,
    gap: theme.spacing.sm,
  },
  saveInput: {
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.sm,
    fontSize: theme.fontSize.md,
    color: theme.colors.text,
  },
  saveBtn: {
    backgroundColor: theme.colors.success,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    alignItems: 'center',
  },
  saveBtnDisabled: {
    opacity: 0.6,
  },
  saveBtnText: {
    color: theme.colors.white,
    fontSize: theme.fontSize.md,
    fontWeight: '600',
  },
  logoutBtn: {
    marginTop: theme.spacing.xl,
    alignItems: 'center',
    padding: theme.spacing.md,
  },
  logoutText: {
    color: theme.colors.textSecondary,
    fontSize: theme.fontSize.md,
  },
});
