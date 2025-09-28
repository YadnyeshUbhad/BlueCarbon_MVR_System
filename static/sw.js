// Service Worker for BlueCarbon MRV PWA
// Provides offline functionality and background sync

const CACHE_NAME = 'bluecarbon-mrv-v1.0.0';
const STATIC_ASSETS = [
    '/',
    '/ngo/dashboard',
    '/ngo/projects/new',
    '/ngo/credits',
    '/admin/',
    '/industry/dashboard',
    '/static/manifest.json'
];

// API endpoints that can work offline with cached data
const API_CACHE_PATTERNS = [
    '/ngo/credits/realtime',
    '/ngo/revenue/realtime',
    '/admin/blockchain/stats'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('[SW] Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[SW] Static assets cached');
                return self.skipWaiting();
            })
            .catch(err => {
                console.error('[SW] Cache installation failed:', err);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[SW] Activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Handle API requests
    if (isAPIRequest(url.pathname)) {
        event.respondWith(handleAPIRequest(request));
        return;
    }
    
    // Handle static assets and pages
    if (request.method === 'GET') {
        event.respondWith(handleStaticRequest(request));
        return;
    }
    
    // Handle form submissions (POST requests) - store for background sync
    if (request.method === 'POST') {
        event.respondWith(handleFormSubmission(request));
        return;
    }
});

// Handle API requests with cache-first strategy for specific endpoints
async function handleAPIRequest(request) {
    const url = new URL(request.url);
    
    // For real-time endpoints, try cache first for offline support
    if (API_CACHE_PATTERNS.some(pattern => url.pathname.includes(pattern))) {
        try {
            const cachedResponse = await caches.match(request);
            if (cachedResponse) {
                // Try to update cache in background
                updateCacheInBackground(request);
                return cachedResponse;
            }
        } catch (err) {
            console.warn('[SW] Cache lookup failed:', err);
        }
    }
    
    // Try network first for API requests
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache successful API responses
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (err) {
        console.warn('[SW] Network request failed:', err);
        
        // Fall back to cache if available
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response
        return new Response(
            JSON.stringify({
                success: false,
                error: 'Offline - data not available',
                offline: true
            }),
            {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

// Handle static requests with cache-first strategy
async function handleStaticRequest(request) {
    try {
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Try network if not in cache
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache successful responses
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (err) {
        console.warn('[SW] Request failed:', err);
        
        // Return offline page if available
        if (request.destination === 'document') {
            const offlineResponse = await caches.match('/offline.html');
            if (offlineResponse) {
                return offlineResponse;
            }
            
            // Create basic offline response
            return new Response(
                `<!DOCTYPE html>
                <html>
                <head>
                    <title>BlueCarbon MRV - Offline</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f8fafc; }
                        .offline-message { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                        .icon { font-size: 48px; margin-bottom: 20px; }
                    </style>
                </head>
                <body>
                    <div class="offline-message">
                        <div class="icon">📡</div>
                        <h1>You're Offline</h1>
                        <p>BlueCarbon MRV is currently offline. Please check your internet connection.</p>
                        <p>Some cached data may still be available.</p>
                        <button onclick="window.location.reload()">Try Again</button>
                    </div>
                </body>
                </html>`,
                {
                    status: 200,
                    headers: { 'Content-Type': 'text/html' }
                }
            );
        }
        
        throw err;
    }
}

// Handle form submissions - store for background sync when offline
async function handleFormSubmission(request) {
    try {
        // Try to submit immediately
        const response = await fetch(request.clone());
        return response;
    } catch (err) {
        console.log('[SW] Form submission failed, storing for background sync:', err);
        
        // Store form data for background sync
        const formData = await request.clone().formData();
        await storeForBackgroundSync({
            url: request.url,
            method: request.method,
            data: Object.fromEntries(formData.entries()),
            timestamp: Date.now()
        });
        
        // Return success response to prevent form resubmission
        return new Response(
            JSON.stringify({
                success: true,
                message: 'Data saved offline. Will sync when connection is restored.',
                offline_stored: true
            }),
            {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

// Background sync for offline form submissions
self.addEventListener('sync', event => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync-forms') {
        event.waitUntil(syncOfflineData());
    } else if (event.tag === 'background-sync-projects') {
        event.waitUntil(syncProjectData());
    }
});

// Push notification handling
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    if (!event.data) {
        console.warn('[SW] Push event has no data');
        return;
    }
    
    try {
        const data = event.data.json();
        const options = {
            body: data.body || 'New update from BlueCarbon MRV',
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/badge-72x72.png',
            tag: data.tag || 'bluecarbon-notification',
            requireInteraction: data.requireInteraction || false,
            actions: data.actions || [{
                action: 'view',
                title: 'View Details'
            }],
            data: data.data || {}
        };
        
        event.waitUntil(
            self.registration.showNotification(
                data.title || 'BlueCarbon MRV',
                options
            )
        );
    } catch (err) {
        console.error('[SW] Error handling push notification:', err);
        
        // Fallback notification
        event.waitUntil(
            self.registration.showNotification(
                'BlueCarbon MRV Update',
                {
                    body: 'You have a new update. Open the app to see details.',
                    icon: '/static/icons/icon-192x192.png',
                    tag: 'bluecarbon-fallback'
                }
            )
        );
    }
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification clicked:', event.notification.tag);
    
    event.notification.close();
    
    const urlToOpen = event.notification.data?.url || '/';
    
    event.waitUntil(
        clients.matchAll({ type: 'window' })
            .then(clientList => {
                // If app is already open, focus on it
                for (let i = 0; i < clientList.length; i++) {
                    const client = clientList[i];
                    if (client.url.includes(urlToOpen) && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Otherwise open new window
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// Background sync functions
async function syncOfflineData() {
    try {
        const offlineData = await getStoredOfflineData();
        
        for (const item of offlineData) {
            try {
                const response = await fetch(item.url, {
                    method: item.method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(item.data)
                });
                
                if (response.ok) {
                    await removeOfflineDataItem(item.id);
                    console.log('[SW] Synced offline data:', item.id);
                }
            } catch (syncError) {
                console.warn('[SW] Failed to sync item:', item.id, syncError);
            }
        }
    } catch (err) {
        console.error('[SW] Background sync failed:', err);
    }
}

async function syncProjectData() {
    try {
        // Sync any pending project updates
        const pendingUpdates = await getStoredProjectUpdates();
        
        for (const update of pendingUpdates) {
            try {
                const response = await fetch('/api/projects/sync', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(update.data)
                });
                
                if (response.ok) {
                    await removePendingProjectUpdate(update.id);
                    console.log('[SW] Synced project update:', update.id);
                }
            } catch (syncError) {
                console.warn('[SW] Failed to sync project update:', update.id, syncError);
            }
        }
    } catch (err) {
        console.error('[SW] Project sync failed:', err);
    }
}

// Storage utility functions
async function getStoredOfflineData() {
    try {
        const db = await openIndexedDB();
        const transaction = db.transaction(['offline_data'], 'readonly');
        const store = transaction.objectStore('offline_data');
        return await getAllFromStore(store);
    } catch (err) {
        console.warn('[SW] Failed to get offline data:', err);
        return [];
    }
}

async function storeForBackgroundSync(data) {
    try {
        const db = await openIndexedDB();
        const transaction = db.transaction(['offline_data'], 'readwrite');
        const store = transaction.objectStore('offline_data');
        
        const item = {
            id: generateUniqueId(),
            ...data,
            stored_at: Date.now()
        };
        
        await addToStore(store, item);
        
        // Register for background sync
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            await self.registration.sync.register('background-sync-forms');
        }
    } catch (err) {
        console.error('[SW] Failed to store offline data:', err);
    }
}

async function removeOfflineDataItem(id) {
    try {
        const db = await openIndexedDB();
        const transaction = db.transaction(['offline_data'], 'readwrite');
        const store = transaction.objectStore('offline_data');
        await deleteFromStore(store, id);
    } catch (err) {
        console.warn('[SW] Failed to remove offline data item:', err);
    }
}

async function getStoredProjectUpdates() {
    try {
        const db = await openIndexedDB();
        const transaction = db.transaction(['project_updates'], 'readonly');
        const store = transaction.objectStore('project_updates');
        return await getAllFromStore(store);
    } catch (err) {
        console.warn('[SW] Failed to get project updates:', err);
        return [];
    }
}

async function removePendingProjectUpdate(id) {
    try {
        const db = await openIndexedDB();
        const transaction = db.transaction(['project_updates'], 'readwrite');
        const store = transaction.objectStore('project_updates');
        await deleteFromStore(store, id);
    } catch (err) {
        console.warn('[SW] Failed to remove project update:', err);
    }
}

// IndexedDB utility functions
function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('BlueCarbon-MRV', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // Create object stores
            if (!db.objectStoreNames.contains('offline_data')) {
                db.createObjectStore('offline_data', { keyPath: 'id' });
            }
            
            if (!db.objectStoreNames.contains('project_updates')) {
                db.createObjectStore('project_updates', { keyPath: 'id' });
            }
        };
    });
}

function getAllFromStore(store) {
    return new Promise((resolve, reject) => {
        const request = store.getAll();
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function addToStore(store, data) {
    return new Promise((resolve, reject) => {
        const request = store.add(data);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function deleteFromStore(store, id) {
    return new Promise((resolve, reject) => {
        const request = store.delete(id);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function generateUniqueId() {
    return 'offline_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Helper functions for API pattern matching
function isAPIRequest(pathname) {
    return pathname.startsWith('/api/') || 
           pathname.startsWith('/ngo/credits/') ||
           pathname.startsWith('/ngo/revenue/') ||
           pathname.startsWith('/admin/blockchain/');
}

// Update cache in background (fire and forget)
function updateCacheInBackground(request) {
    fetch(request.clone())
        .then(response => {
            if (response.ok) {
                return caches.open(CACHE_NAME)
                    .then(cache => cache.put(request, response));
            }
        })
        .catch(err => console.warn('[SW] Background cache update failed:', err));
}

console.log('[SW] Service Worker loaded with enhanced PWA features');
    
    if (event.tag === 'bluecarbon-form-sync') {
        event.waitUntil(syncStoredForms());
    }
});

// Store data for background sync
async function storeForBackgroundSync(data) {
    const db = await openIndexedDB();
    const tx = db.transaction(['sync_queue'], 'readwrite');
    const store = tx.objectStore('sync_queue');
    
    await store.add({
        id: Date.now() + Math.random(),
        data: data,
        synced: false
    });
    
    // Register for background sync
    try {
        await self.registration.sync.register('bluecarbon-form-sync');
        console.log('[SW] Registered for background sync');
    } catch (err) {
        console.warn('[SW] Background sync registration failed:', err);
    }
}

// Sync stored forms when connection is restored
async function syncStoredForms() {
    try {
        const db = await openIndexedDB();
        const tx = db.transaction(['sync_queue'], 'readwrite');
        const store = tx.objectStore('sync_queue');
        
        const unsyncedItems = await store.getAll();
        const pendingItems = unsyncedItems.filter(item => !item.synced);
        
        console.log(`[SW] Syncing ${pendingItems.length} stored items`);
        
        for (const item of pendingItems) {
            try {
                const formData = new FormData();
                for (const [key, value] of Object.entries(item.data.data)) {
                    formData.append(key, value);
                }
                
                const response = await fetch(item.data.url, {
                    method: item.data.method,
                    body: formData
                });
                
                if (response.ok) {
                    // Mark as synced
                    await store.delete(item.id);
                    console.log('[SW] Successfully synced item:', item.id);
                } else {
                    console.warn('[SW] Sync failed for item:', item.id, response.status);
                }
            } catch (err) {
                console.error('[SW] Error syncing item:', item.id, err);
            }
        }
    } catch (err) {
        console.error('[SW] Sync process failed:', err);
    }
}

// Open IndexedDB for storing offline data
function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('BlueCarbon_OfflineDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            if (!db.objectStoreNames.contains('sync_queue')) {
                db.createObjectStore('sync_queue', { keyPath: 'id' });
            }
        };
    });
}

// Update cache in background
async function updateCacheInBackground(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            await cache.put(request, response);
        }
    } catch (err) {
        // Silently fail - cache update is not critical
        console.debug('[SW] Background cache update failed:', err);
    }
}

// Check if request is for API endpoint
function isAPIRequest(pathname) {
    return pathname.startsWith('/api/') || 
           pathname.includes('/realtime') ||
           pathname.includes('/upload/') ||
           pathname.includes('/calculate/') ||
           pathname.includes('/blockchain/') ||
           pathname.includes('/satellite/') ||
           pathname.includes('/forecast/');
}

// Push notification handling for updates
self.addEventListener('push', event => {
    if (!event.data) return;
    
    try {
        const data = event.data.json();
        
        event.waitUntil(
            self.registration.showNotification(data.title || 'BlueCarbon MRV Update', {
                body: data.body || 'New update available',
                icon: '/static/manifest.json',
                badge: '/static/manifest.json',
                tag: 'bluecarbon-update',
                renotify: true,
                requireInteraction: false,
                actions: [
                    {
                        action: 'view',
                        title: 'View',
                        icon: '/static/manifest.json'
                    },
                    {
                        action: 'dismiss',
                        title: 'Dismiss'
                    }
                ]
            })
        );
    } catch (err) {
        console.error('[SW] Push notification error:', err);
    }
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

console.log('[SW] Service Worker loaded successfully');