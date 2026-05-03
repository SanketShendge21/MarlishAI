import { CACHE_MAX_ENTRIES, CACHE_TTL_DAYS } from './constants';

const DB_NAME = 'marlish-ai-cache';
const DB_VERSION = 2; // Incremented version to add history store
const STORE_NAME = 'translations';
const HISTORY_STORE = 'history';

// Generate a simple hash for cache keys
async function generateHash(message) {
  const msgUint8 = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

export function normalizeText(text) {
  return text
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[.,!?]+$/, '')
    .trim();
}

async function getDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'key' });
        store.createIndex('timestamp', 'timestamp', { unique: false });
      }
      if (!db.objectStoreNames.contains(HISTORY_STORE)) {
        const historyStore = db.createObjectStore(HISTORY_STORE, { keyPath: 'id', autoIncrement: true });
        historyStore.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
  });
}

export async function initCache() {
  try {
    await getDB();
    return true;
  } catch (error) {
    console.error('Failed to initialize cache:', error);
    return false;
  }
}

export async function getCached(input, source, target) {
  if (!input) return null;
  
  try {
    const normalizedInput = normalizeText(input);
    const keyString = `${source}-${target}-${normalizedInput}`;
    const key = await generateHash(keyString);
    
    const db = await getDB();
    const transaction = db.transaction(STORE_NAME, 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    
    return new Promise((resolve, reject) => {
      const request = store.get(key);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const result = request.result;
        if (!result) return resolve(null);
        
        // Check TTL
        const ageInDays = (Date.now() - result.timestamp) / (1000 * 60 * 60 * 24);
        if (ageInDays > CACHE_TTL_DAYS) {
          // Delete expired entry
          const deleteTx = db.transaction(STORE_NAME, 'readwrite');
          deleteTx.objectStore(STORE_NAME).delete(key);
          return resolve(null);
        }
        
        resolve(result.output);
      };
    });
  } catch (error) {
    console.warn('Cache read error:', error);
    return null;
  }
}

export async function setCached(input, source, target, output, tier) {
  if (!input || !output) return;
  
  try {
    const normalizedInput = normalizeText(input);
    const keyString = `${source}-${target}-${normalizedInput}`;
    const key = await generateHash(keyString);
    
    const db = await getDB();
    
    // Check limit and evict if necessary
    const countTx = db.transaction(STORE_NAME, 'readonly');
    const countRequest = countTx.objectStore(STORE_NAME).count();
    
    countRequest.onsuccess = () => {
      if (countRequest.result >= CACHE_MAX_ENTRIES) {
        // Evict oldest
        const evictTx = db.transaction(STORE_NAME, 'readwrite');
        const evictStore = evictTx.objectStore(STORE_NAME);
        const index = evictStore.index('timestamp');
        const cursorRequest = index.openCursor();
        
        cursorRequest.onsuccess = (e) => {
          const cursor = e.target.result;
          if (cursor) {
            evictStore.delete(cursor.primaryKey);
          }
        };
      }
      
      // Save new entry
      const saveTx = db.transaction(STORE_NAME, 'readwrite');
      saveTx.objectStore(STORE_NAME).put({
        key,
        source,
        target,
        input,
        output,
        tier,
        timestamp: Date.now()
      });
    };
  } catch (error) {
    console.warn('Cache write error:', error);
  }
}

export async function clearCache() {
  try {
    const db = await getDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).clear();
    return true;
  } catch (error) {
    console.error('Cache clear error:', error);
    return false;
  }
}

// =======================
// History Storage
// =======================

export async function addToHistory(input, output, source, target, tier) {
  if (!input || !output || tier === 0) return;
  
  try {
    const db = await getDB();
    
    // Check limit and evict if > 50 entries
    const countTx = db.transaction(HISTORY_STORE, 'readonly');
    const countRequest = countTx.objectStore(HISTORY_STORE).count();
    
    countRequest.onsuccess = () => {
      if (countRequest.result >= 50) {
        // Evict oldest
        const evictTx = db.transaction(HISTORY_STORE, 'readwrite');
        const evictStore = evictTx.objectStore(HISTORY_STORE);
        const index = evictStore.index('timestamp');
        const cursorRequest = index.openCursor();
        
        cursorRequest.onsuccess = (e) => {
          const cursor = e.target.result;
          if (cursor) {
            evictStore.delete(cursor.primaryKey);
          }
        };
      }
      
      // Save new entry
      const saveTx = db.transaction(HISTORY_STORE, 'readwrite');
      saveTx.objectStore(HISTORY_STORE).add({
        input,
        output,
        source,
        target,
        tier,
        timestamp: Date.now()
      });
    };
  } catch (error) {
    console.warn('History write error:', error);
  }
}

export async function getHistory(limit = 20) {
  try {
    const db = await getDB();
    const tx = db.transaction(HISTORY_STORE, 'readonly');
    const store = tx.objectStore(HISTORY_STORE);
    const index = store.index('timestamp');
    
    return new Promise((resolve, reject) => {
      // Use prev cursor to get newest first
      const request = index.openCursor(null, 'prev');
      const results = [];
      
      request.onerror = () => reject(request.error);
      request.onsuccess = (e) => {
        const cursor = e.target.result;
        if (cursor && results.length < limit) {
          results.push(cursor.value);
          cursor.continue();
        } else {
          resolve(results);
        }
      };
    });
  } catch (error) {
    console.warn('History read error:', error);
    return [];
  }
}

export async function clearHistory() {
  try {
    const db = await getDB();
    const tx = db.transaction(HISTORY_STORE, 'readwrite');
    tx.objectStore(HISTORY_STORE).clear();
    return true;
  } catch (error) {
    console.error('History clear error:', error);
    return false;
  }
}
