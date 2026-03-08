/**
 * Language Learning page.
 */
async function loadLanguage(container) {
  container.innerHTML = `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- YouTube extractor -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 class="font-semibold text-white mb-4">🎬 Extract from YouTube</h3>
        <div class="space-y-3">
          <input type="url" id="yt-url" placeholder="https://www.youtube.com/watch?v=..."
            class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <select id="yt-lang" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
            <option value="english">🇬🇧 English</option>
            <option value="korean">🇰🇷 Korean</option>
          </select>
          <button id="yt-extract-btn"
            class="w-full bg-red-600 hover:bg-red-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors">
            🎬 Extract Vocabulary
          </button>
        </div>
      </div>

      <!-- File upload -->
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 class="font-semibold text-white mb-4">📄 Upload Transcript</h3>
        <div class="space-y-3">
          <textarea id="upload-content" rows="4" placeholder="Paste .srt or plain text transcript here…"
            class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
          <select id="upload-lang" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
            <option value="english">🇬🇧 English</option>
            <option value="korean">🇰🇷 Korean</option>
          </select>
          <button id="upload-extract-btn"
            class="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors">
            📄 Process Transcript
          </button>
        </div>
      </div>
    </div>

    <!-- Vocabulary filters -->
    <div class="flex flex-wrap gap-3 mb-4">
      <select id="vocab-lang-filter" class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
        <option value="">All Languages</option>
        <option value="english">English</option>
        <option value="korean">Korean</option>
      </select>
      <select id="vocab-learned-filter" class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
        <option value="">All</option>
        <option value="false">Not Learned</option>
        <option value="true">Learned</option>
      </select>
      <button id="vocab-filter-btn"
        class="bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-4 py-2 text-sm transition-colors">Filter</button>
      <div class="ml-auto text-sm text-gray-400 self-center" id="vocab-stats">Loading stats…</div>
    </div>

    <!-- Vocabulary table -->
    <div class="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-800">
              <th class="text-left px-4 py-3 text-gray-400 font-medium">Word</th>
              <th class="text-left px-4 py-3 text-gray-400 font-medium">Language</th>
              <th class="text-left px-4 py-3 text-gray-400 font-medium">POS</th>
              <th class="text-left px-4 py-3 text-gray-400 font-medium">Frequency</th>
              <th class="text-left px-4 py-3 text-gray-400 font-medium">Difficulty</th>
              <th class="text-left px-4 py-3 text-gray-400 font-medium">Status</th>
              <th class="text-left px-4 py-3 text-gray-400 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody id="vocab-table-body">
            <tr><td colspan="7" class="text-center text-gray-500 py-8">Loading vocabulary…</td></tr>
          </tbody>
        </table>
      </div>
    </div>`;

  const renderVocab = async () => {
    const lang = document.getElementById('vocab-lang-filter').value;
    const learned = document.getElementById('vocab-learned-filter').value;
    const params = new URLSearchParams();
    if (lang) params.append('language', lang);
    if (learned !== '') params.append('learned', learned);
    const qs = params.toString() ? `?${params}` : '';

    try {
      const vocab = await api.language.vocabulary(qs);
      state.set('vocabulary', vocab);
      const body = document.getElementById('vocab-table-body');
      const diffLabels = ['', '⭐', '⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐'];

      if (vocab.length === 0) {
        body.innerHTML = '<tr><td colspan="7" class="text-center text-gray-500 py-8">No vocabulary yet. Extract from YouTube or upload a transcript!</td></tr>';
        return;
      }

      body.innerHTML = vocab.map(v => `
        <tr class="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
          <td class="px-4 py-3 font-medium text-white">${v.word}</td>
          <td class="px-4 py-3 text-gray-400">${v.language}</td>
          <td class="px-4 py-3 text-gray-400">${v.pos || '—'}</td>
          <td class="px-4 py-3 text-gray-400">${v.frequency_count}</td>
          <td class="px-4 py-3">${diffLabels[v.difficulty] || '—'}</td>
          <td class="px-4 py-3">
            ${v.learned
              ? '<span class="text-xs bg-green-900/50 text-green-300 px-2 py-0.5 rounded-full">✓ Learned</span>'
              : '<span class="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded-full">Not Learned</span>'}
          </td>
          <td class="px-4 py-3">
            <div class="flex gap-2">
              ${!v.learned ? `<button class="text-xs text-green-400 hover:text-green-300" onclick="markLearned('${v.id}')">✓ Learned</button>` : ''}
              <button class="text-xs text-indigo-400 hover:text-indigo-300" onclick="addToFlashcard('${v.id}', '${v.word}')">+ Card</button>
            </div>
          </td>
        </tr>`).join('');
    } catch (e) {
      toast.error('Failed to load vocabulary: ' + e.message);
    }
  };

  const updateStats = async () => {
    try {
      const data = await api.language.analytics();
      const stats = document.getElementById('vocab-stats');
      if (stats) stats.textContent = `${data.total_words} words · ${data.learned_words} learned · ${data.learning_rate}%`;
    } catch (_) {}
  };

  await Promise.all([renderVocab(), updateStats()]);

  document.getElementById('vocab-filter-btn')?.addEventListener('click', renderVocab);

  document.getElementById('yt-extract-btn')?.addEventListener('click', async () => {
    const url = document.getElementById('yt-url').value.trim();
    const language = document.getElementById('yt-lang').value;
    if (!url) { toast.warning('Please enter a YouTube URL'); return; }
    const btn = document.getElementById('yt-extract-btn');
    btn.textContent = '⏳ Extracting…';
    btn.disabled = true;
    try {
      await api.language.extractYouTube({ url, language });
      toast.success('Vocabulary extracted successfully!');
      await renderVocab();
      await updateStats();
    } catch (e) {
      toast.error('Extraction failed: ' + e.message);
    } finally {
      btn.textContent = '🎬 Extract Vocabulary';
      btn.disabled = false;
    }
  });

  document.getElementById('upload-extract-btn')?.addEventListener('click', async () => {
    const content = document.getElementById('upload-content').value.trim();
    const language = document.getElementById('upload-lang').value;
    if (!content) { toast.warning('Please paste some text'); return; }
    const btn = document.getElementById('upload-extract-btn');
    btn.textContent = '⏳ Processing…';
    btn.disabled = true;
    try {
      await api.language.extractUpload({ content, language });
      toast.success('Vocabulary extracted successfully!');
      await renderVocab();
      await updateStats();
    } catch (e) {
      toast.error('Processing failed: ' + e.message);
    } finally {
      btn.textContent = '📄 Process Transcript';
      btn.disabled = false;
    }
  });

  window.markLearned = async (id) => {
    try {
      await api.language.markLearned(id);
      toast.success('Marked as learned! 🎉');
      await renderVocab();
      await updateStats();
    } catch (e) { toast.error(e.message); }
  };

  window.addToFlashcard = async (id, word) => {
    const decks = await api.decks.list().catch(() => []);
    if (decks.length === 0) {
      toast.info('Please create a flashcard deck first.');
      return;
    }
    modal.form(`Add "${word}" to Flashcard`, [
      { name: 'deck_id', label: 'Deck', type: 'select', value: decks[0].id,
        options: decks.map(d => ({value: d.id, label: d.name})) },
      { name: 'back', label: 'Back (Translation/Definition)', type: 'textarea', placeholder: 'Translation or definition…' },
    ], async (data) => {
      try {
        await api.cards.create({ deck_id: data.deck_id, front: word, back: data.back });
        toast.success('Added to flashcard deck!');
      } catch (e) { toast.error(e.message); }
    });
  };
}

window.pages = window.pages || {};
window.pages.language = loadLanguage;
