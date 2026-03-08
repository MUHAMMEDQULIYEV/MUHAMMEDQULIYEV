/**
 * Toast notification component.
 */
const toast = {
  show(message, type = 'success', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const colorMap = {
      success: 'bg-green-600',
      error:   'bg-red-600',
      info:    'bg-indigo-600',
      warning: 'bg-yellow-600',
    };

    const iconMap = {
      success: '✅',
      error:   '❌',
      info:    'ℹ️',
      warning: '⚠️',
    };

    const el = document.createElement('div');
    el.className = `toast pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg text-white text-sm max-w-sm ${colorMap[type] || colorMap.info}`;
    el.innerHTML = `<span>${iconMap[type] || ''}</span><span>${message}</span>`;
    container.appendChild(el);

    setTimeout(() => el.remove(), duration);
  },

  success: (msg) => toast.show(msg, 'success'),
  error:   (msg) => toast.show(msg, 'error'),
  info:    (msg) => toast.show(msg, 'info'),
  warning: (msg) => toast.show(msg, 'warning'),
};

window.toast = toast;
