/**
 * API wrapper for all backend calls.
 */
const API_BASE = '/api';

const api = {
  async request(method, path, body = null) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body !== null) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    if (res.status === 204) return null;
    return res.json();
  },

  get:    (path)        => api.request('GET',    path),
  post:   (path, body)  => api.request('POST',   path, body),
  put:    (path, body)  => api.request('PUT',    path, body),
  delete: (path)        => api.request('DELETE', path),

  // Tasks
  tasks: {
    list:     (params = '') => api.get(`/tasks${params}`),
    get:      (id)          => api.get(`/tasks/${id}`),
    upcoming: ()            => api.get('/tasks/upcoming'),
    create:   (data)        => api.post('/tasks', data),
    update:   (id, data)    => api.put(`/tasks/${id}`, data),
    remove:   (id)          => api.delete(`/tasks/${id}`),
  },

  // Notes
  notes: {
    list:   ()          => api.get('/notes'),
    search: (q)         => api.get(`/notes/search?q=${encodeURIComponent(q)}`),
    create: (data)      => api.post('/notes', data),
    update: (id, data)  => api.put(`/notes/${id}`, data),
    remove: (id)        => api.delete(`/notes/${id}`),
  },

  // Flashcards
  decks: {
    list:   ()      => api.get('/decks'),
    create: (data)  => api.post('/decks', data),
  },
  cards: {
    review:  (deckId)       => api.get(`/cards/review/${deckId}`),
    create:  (data)         => api.post('/cards', data),
    submit:  (id, quality)  => api.put(`/cards/${id}/review`, { quality }),
    remove:  (id)           => api.delete(`/cards/${id}`),
  },

  // Language
  language: {
    extractYouTube: (data) => api.post('/language/extract-youtube', data),
    extractUpload:  (data) => api.post('/language/extract-upload',  data),
    vocabulary:     (params = '') => api.get(`/language/vocabulary${params}`),
    analytics:      ()     => api.get('/language/analytics'),
    markLearned:    (id)   => api.post(`/language/vocabulary/${id}/mark-learned`, {}),
  },

  // Analytics
  analytics: {
    productivity:    () => api.get('/analytics/productivity'),
    language:        () => api.get('/analytics/language'),
    dashboard:       () => api.get('/analytics/dashboard'),
    recommendations: () => api.get('/analytics/recommendations'),
  },

  // Notifications
  notifications: {
    settings: (data) => api.post('/notifications/settings', data),
    queue:    ()     => api.get('/notifications/queue'),
    sendEmail:(data) => api.post('/notifications/send-email', data),
  },

  // Calendar
  calendar: {
    sync:       (data) => api.post('/calendar/sync', data || {}),
    taskToEvent:(data) => api.post('/calendar/task-to-event', data),
    events:     ()     => api.get('/calendar/events'),
  },
};

window.api = api;
