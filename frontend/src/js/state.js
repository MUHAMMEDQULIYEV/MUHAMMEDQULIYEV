/**
 * Simple client-side state store.
 */
const state = {
  tasks: [],
  notes: [],
  decks: [],
  vocabulary: [],
  currentDeck: null,
  reviewCards: [],
  reviewIndex: 0,

  _listeners: {},

  on(event, fn) {
    if (!this._listeners[event]) this._listeners[event] = [];
    this._listeners[event].push(fn);
  },

  emit(event, data) {
    (this._listeners[event] || []).forEach(fn => fn(data));
  },

  set(key, value) {
    this[key] = value;
    this.emit(key, value);
  },
};

window.state = state;
