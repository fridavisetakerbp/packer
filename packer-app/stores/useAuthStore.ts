import { create } from 'zustand';
import { User } from 'firebase/auth';
import { onAuthChange } from '@/services/auth';

interface AuthState {
  user: User | null;
  loading: boolean;
  initialized: boolean;
  init: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  initialized: false,
  init: () => {
    onAuthChange((user) => {
      set({ user, loading: false, initialized: true });
    });
  },
}));
