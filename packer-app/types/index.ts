export interface PackingList {
  id: string;
  name: string;
  items: Record<string, boolean>;
  createdAt: number;
  updatedAt: number;
}

export interface ActivityModule {
  id: string;
  name: string;
  items: string[];
}

export interface Defaults {
  daily: string[];
  base: string[];
  base_sleepover: string[];
}
