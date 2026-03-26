import { create } from 'zustand';

interface AppState {
  sidebarOpen: boolean;
  activeStoreId: string | null;
  currentMode: 'demo' | 'shopify';
  toggleSidebar: () => void;
  setActiveStoreId: (id: string | null) => void;
  setCurrentMode: (mode: 'demo' | 'shopify') => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarOpen: true,
  activeStoreId: null,
  currentMode: 'demo',
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setActiveStoreId: (id) => set({ activeStoreId: id }),
  setCurrentMode: (mode) => set({ currentMode: mode }),
}));
