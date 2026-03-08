/**
 * Notes page.
 */
async function loadNotes(container) {
  container.innerHTML = `
    <div class="flex items-center gap-3 mb-6">
      <input type="text" id="notes-search" placeholder="Search notes…"
        class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <button id="search-btn"
        class="bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-4 py-2 text-sm transition-colors">🔍</button>
      <button id="add-note-btn"
        class="bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors">
        + New Note
      </button>
    </div>
    <div id="notes-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="text-gray-500 text-sm">Loading…</div>
    </div>`;

  const renderNotes = async (searchQuery = null) => {
    try {
      const notes = searchQuery
        ? await api.notes.search(searchQuery)
        : await api.notes.list();
      state.set('notes', notes);
      const grid = document.getElementById('notes-grid');

      if (notes.length === 0) {
        grid.innerHTML = '<div class="text-gray-500 text-sm col-span-3 text-center py-12">No notes yet. Create your first note! 📝</div>';
        return;
      }

      grid.innerHTML = notes.map(n => {
        // Safely extract plain text using a temporary DOM element
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = n.content || '';
        const preview = tempDiv.textContent.slice(0, 150);
        const tags = (n.tags || []).map(t => `<span class="text-xs bg-indigo-900/50 text-indigo-300 px-2 py-0.5 rounded-full">${t}</span>`).join(' ');
        const date = new Date(n.updated_at).toLocaleDateString();
        return `
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-indigo-500 transition-colors group cursor-pointer"
               onclick="editNote('${n.id}')">
            <div class="flex items-start justify-between gap-2 mb-2">
              <h3 class="font-semibold text-white text-sm flex-1">${n.title}</h3>
              <button class="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 text-xs transition-opacity"
                onclick="event.stopPropagation(); deleteNote('${n.id}')">✕</button>
            </div>
            ${preview ? `<p class="text-gray-400 text-xs mb-3 line-clamp-3">${preview}</p>` : ''}
            <div class="flex items-center justify-between">
              <div class="flex flex-wrap gap-1">${tags}</div>
              <span class="text-xs text-gray-600">${date}</span>
            </div>
          </div>`;
      }).join('');
    } catch (e) {
      toast.error('Failed to load notes: ' + e.message);
    }
  };

  await renderNotes();

  document.getElementById('search-btn')?.addEventListener('click', () => {
    const q = document.getElementById('notes-search').value.trim();
    renderNotes(q || null);
  });

  document.getElementById('notes-search')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const q = e.target.value.trim();
      renderNotes(q || null);
    }
  });

  document.getElementById('add-note-btn')?.addEventListener('click', () => {
    modal.form('New Note', [
      { name: 'title', label: 'Title', placeholder: 'Note title…' },
      { name: 'content', label: 'Content', type: 'textarea', placeholder: 'Write your note…' },
      { name: 'tags', label: 'Tags (comma separated)', placeholder: 'study, english, vocabulary' },
    ], async (data) => {
      try {
        const tags = data.tags ? data.tags.split(',').map(t => t.trim()).filter(Boolean) : [];
        await api.notes.create({ title: data.title, content: data.content, tags });
        toast.success('Note created!');
        await renderNotes();
      } catch (e) { toast.error(e.message); }
    });
  });

  window.editNote = (id) => {
    const note = state.notes.find(n => n.id === id);
    if (!note) return;
    modal.form('Edit Note', [
      { name: 'title', label: 'Title', value: note.title },
      { name: 'content', label: 'Content', type: 'textarea', value: note.content || '' },
      { name: 'tags', label: 'Tags (comma separated)', value: (note.tags || []).join(', ') },
    ], async (data) => {
      try {
        const tags = data.tags ? data.tags.split(',').map(t => t.trim()).filter(Boolean) : [];
        await api.notes.update(id, { title: data.title, content: data.content, tags });
        toast.success('Note updated!');
        await renderNotes();
      } catch (e) { toast.error(e.message); }
    });
  };

  window.deleteNote = async (id) => {
    if (!confirm('Delete this note?')) return;
    try {
      await api.notes.remove(id);
      toast.success('Note deleted.');
      await renderNotes();
    } catch (e) { toast.error(e.message); }
  };
}

window.pages = window.pages || {};
window.pages.notes = loadNotes;
