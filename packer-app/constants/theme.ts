export const theme = {
  colors: {
    background: '#ffe4ec',
    primary: '#e91e63',
    primaryLight: '#f8bbd0',
    text: '#333',
    textSecondary: '#888',
    textMuted: '#b0b0b0',
    white: '#fff',
    border: '#f0c0d0',
    danger: '#d32f2f',
    success: '#4caf50',
    cardBackground: '#fff',
    inputBackground: '#fff',
    tabBar: '#fff',
    headerBackground: '#e91e63',
    headerText: '#fff',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  borderRadius: {
    sm: 6,
    md: 10,
    lg: 16,
  },
  fontSize: {
    sm: 13,
    md: 16,
    lg: 20,
    xl: 26,
  },
};

export const DEFAULT_MODULES: Record<string, string[]> = {
  'Running': ['running shoes', 'sports socks', 'shorts', 't-shirt'],
  'Swimming': ['swimsuit', 'towel', 'flip flops'],
  'Hiking': ['hiking boots', 'backpack', 'water bottle', 'jacket'],
  'Sleeping': ['pajamas'],
  'Work meetings': ['formal shirt', 'formal pants', 'belt', 'dress shoes'],
  'Coding sessions': ['laptop', 'charger', 'notebook'],
  'Dinner out': ['nice outfit', 'casual shoes'],
};

export const DEFAULT_DEFAULTS = {
  daily: ['underwear', 'socks', 't-shirt'],
  base: ['toothbrush', 'toiletries'],
  base_sleepover: [] as string[],
};
