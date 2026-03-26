import {
  collection,
  doc,
  getDoc,
  setDoc,
  updateDoc,
  deleteDoc,
  onSnapshot,
  query,
  orderBy,
  Unsubscribe,
} from 'firebase/firestore';
import { db } from './firebase';
import { PackingList, ActivityModule, Defaults } from '@/types';

function userRef(userId: string) {
  return doc(db, 'users', userId);
}

// --- Defaults ---

export function subscribeDefaults(
  userId: string,
  callback: (defaults: Defaults) => void
): Unsubscribe {
  return onSnapshot(doc(db, 'users', userId, 'settings', 'defaults'), (snap) => {
    if (snap.exists()) {
      callback(snap.data() as Defaults);
    }
  });
}

export async function getDefaults(userId: string): Promise<Defaults | null> {
  const snap = await getDoc(doc(db, 'users', userId, 'settings', 'defaults'));
  return snap.exists() ? (snap.data() as Defaults) : null;
}

export async function setDefaults(userId: string, defaults: Defaults) {
  await setDoc(doc(db, 'users', userId, 'settings', 'defaults'), defaults);
}

// --- Modules ---

export function subscribeModules(
  userId: string,
  callback: (modules: ActivityModule[]) => void
): Unsubscribe {
  const q = query(
    collection(db, 'users', userId, 'modules'),
    orderBy('name')
  );
  return onSnapshot(q, (snap) => {
    const modules = snap.docs.map((d) => ({ id: d.id, ...d.data() } as ActivityModule));
    callback(modules);
  });
}

export async function createModule(userId: string, mod: Omit<ActivityModule, 'id'>) {
  const ref = doc(collection(db, 'users', userId, 'modules'));
  await setDoc(ref, mod);
  return ref.id;
}

export async function updateModule(userId: string, moduleId: string, data: Partial<ActivityModule>) {
  const { id, ...rest } = data as any;
  await updateDoc(doc(db, 'users', userId, 'modules', moduleId), rest);
}

export async function deleteModule(userId: string, moduleId: string) {
  await deleteDoc(doc(db, 'users', userId, 'modules', moduleId));
}

// --- Packing Lists ---

export function subscribeLists(
  userId: string,
  callback: (lists: PackingList[]) => void
): Unsubscribe {
  const q = query(
    collection(db, 'users', userId, 'lists'),
    orderBy('updatedAt', 'desc')
  );
  return onSnapshot(q, (snap) => {
    const lists = snap.docs.map((d) => ({ id: d.id, ...d.data() } as PackingList));
    callback(lists);
  });
}

export async function createList(userId: string, list: Omit<PackingList, 'id'>) {
  const ref = doc(collection(db, 'users', userId, 'lists'));
  await setDoc(ref, list);
  return ref.id;
}

export async function updateList(userId: string, listId: string, data: Partial<PackingList>) {
  const { id, ...rest } = data as any;
  await updateDoc(doc(db, 'users', userId, 'lists', listId), rest);
}

export async function deleteList(userId: string, listId: string) {
  await deleteDoc(doc(db, 'users', userId, 'lists', listId));
}
