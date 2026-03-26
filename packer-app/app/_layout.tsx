import { useFonts } from 'expo-font';
import { Stack, useRouter, useSegments } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import 'react-native-reanimated';

import { useAuthStore } from '@/stores/useAuthStore';
import { usePackingStore } from '@/stores/usePackingStore';

export {
  ErrorBoundary,
} from 'expo-router';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
  });

  const initAuth = useAuthStore((s) => s.init);
  const initialized = useAuthStore((s) => s.initialized);

  useEffect(() => {
    initAuth();
  }, []);

  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded && initialized) {
      SplashScreen.hideAsync();
    }
  }, [loaded, initialized]);

  if (!loaded || !initialized) {
    return null;
  }

  return <RootLayoutNav />;
}

function RootLayoutNav() {
  const user = useAuthStore((s) => s.user);
  const subscribe = usePackingStore((s) => s.subscribe);
  const unsubscribe = usePackingStore((s) => s.unsubscribe);
  const router = useRouter();
  const segments = useSegments();

  // Subscribe to Firestore when user logs in
  useEffect(() => {
    if (user) {
      subscribe(user.uid);
    }
    return () => unsubscribe();
  }, [user?.uid]);

  // Auth guard: redirect based on auth state
  useEffect(() => {
    const inAuthGroup = segments[0] === '(auth)';

    if (!user && !inAuthGroup) {
      router.replace('/(auth)/login');
    } else if (user && inAuthGroup) {
      router.replace('/(tabs)');
    }
  }, [user, segments]);

  return (
    <Stack>
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="list/[id]" options={{ title: 'Packing List' }} />
      <Stack.Screen name="module/[id]" options={{ title: 'Module' }} />
      <Stack.Screen name="create-module" options={{ title: 'Create Module' }} />
    </Stack>
  );
}
