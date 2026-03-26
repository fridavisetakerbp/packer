import { create } from 'zustand';
import { PackingList, ActivityModule, Defaults } from '@/types';
import { DEFAULT_DEFAULTS, DEFAULT_MODULES } from '@/constants/theme';
import * as fs from '@/services/firestore';
import { Unsubscribe } from 'firebase/firestore';

interface PackingState {
  defaults: Defaults;
  modules: ActivityModule[];
  lists: PackingList[];
  loading: boolean;

  // Subscription management
  _unsubscribers: Unsubscribe[];
  subscribe: (userId: string) => void;
  unsubscribe: () => void;

  // Seed defaults for new users
  seedDefaults: (userId: string) => Promise<void>;

  // Defaults
  updateDefaults: (userId: string, defaults: Defaults) => Promise<void>;

  // Modules
  createModule: (userId: string, name: string, items: string[]) => Promise<string>;
  updateModule: (userId: string, moduleId: string, data: Partial<ActivityModule>) => Promise<void>;
  deleteModule: (userId: string, moduleId: string) => Promise<void>;

  // Lists
  createList: (userId: string, name: string, items: Record<string, boolean>) => Promise<string>;
  updateList: (userId: string, listId: string, data: Partial<PackingList>) => Promise<void>;
  deleteList: (userId: string, listId: string) => Promise<void>;
}

export const usePackingStore = create<PackingState>((set, get) => ({
  defaults: DEFAULT_DEFAULTS,
  modules: [],
  lists: [],
  loading: true,
  _unsubscribers: [],

  subscribe: (userId: string) => {
    // Clean up existing subscriptions
    get().unsubscribe();

    const unsub1 = fs.subscribeDefaults(userId, (defaults) => {
      set({ defaults });
    });

    const unsub2 = fs.subscribeModules(userId, (modules) => {
      set({ modules, loading: false });
    });

    const unsub3 = fs.subscribeLists(userId, (lists) => {
      set({ lists });
    });

    set({ _unsubscribers: [unsub1, unsub2, unsub3] });
  },

  unsubscribe: () => {
    get()._unsubscribers.forEach((unsub) => unsub());
    set({ _unsubscribers: [], loading: true });
  },

  seedDefaults: async (userId: string) => {
    const existing = await fs.getDefaults(userId);
    if (!existing) {
      await fs.setDefaults(userId, DEFAULT_DEFAULTS);
      for (const [name, items] of Object.entries(DEFAULT_MODULES)) {
        await fs.createModule(userId, { name, items });
      }
    }
  },

  updateDefaults: async (userId, defaults) => {
    await fs.setDefaults(userId, defaults);
  },

  createModule: async (userId, name, items) => {
    return fs.createModule(userId, { name, items });
  },

  updateModule: async (userId, moduleId, data) => {
    await fs.updateModule(userId, moduleId, data);
  },

  deleteModule: async (userId, moduleId) => {
    await fs.deleteModule(userId, moduleId);
  },

  createList: async (userId, name, items) => {
    const now = Date.now();
    return fs.createList(userId, { name, items, createdAt: now, updatedAt: now });
  },

  updateList: async (userId, listId, data) => {
    await fs.updateList(userId, listId, { ...data, updatedAt: Date.now() });
  },

  deleteList: async (userId, listId) => {
    await fs.deleteList(userId, listId);
  },
}));
