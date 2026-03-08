/**
 * App bootstrap & router.
 * Connects Alpine.js navigation to page loaders.
 */

window.loadPage = function(page, container) {
  const loader = window.pages && window.pages[page];
  if (typeof loader === 'function') {
    loader(container).catch(err => {
      console.error(`Error loading page ${page}:`, err);
      if (window.toast) toast.error(`Error loading ${page}: ${err.message}`);
    });
  }
};

// Check API health on startup
window.addEventListener('DOMContentLoaded', async () => {
  try {
    const health = await fetch('/api/health');
    if (!health.ok) {
      toast.warning('Backend is not responding. Please wait a moment and refresh.');
    }
  } catch (_) {
    toast.warning('Cannot reach backend. Ensure Docker is running.');
  }
});
