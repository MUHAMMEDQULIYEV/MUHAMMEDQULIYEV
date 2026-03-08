/**
 * Flashcards page with SM-2 spaced repetition study mode.
 */
let currentStudyDeck = null;
let currentDeckName = '';
let reviewCards = [];
let reviewIndex = 0;
let cardFlipped = false;

async function loadFlashcards(container) {
  container.innerHTML = `
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-semibold text-white">My Decks</h2>
      <button id="add-deck-btn"
        class="bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors">
        + New Deck
      </button>
    </div>
    <div id="decks-list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="text-gray-500 text-sm">Loading…</div>
    </div>
    <div id="study-mode" class="hidden"></div>`;

  const renderDecks = async () => {
    try {
      const decks = await api.decks.list();
      const list = document.getElementById('decks-list');
      if (decks.length === 0) {
        list.innerHTML = '<div class="text-gray-500 text-sm col-span-3 text-center py-12">No decks yet. Create your first deck! 🃏</div>';
        return;
      }
      list.innerHTML = decks.map(d => `
        <div class="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-indigo-500 transition-colors group">
          <div class="flex items-start justify-between mb-3">
            <div>
              <h3 class="font-semibold text-white">${d.name}</h3>
              <span class="text-xs text-gray-400">${d.language} · ${d.source_type}</span>
            </div>
            <span class="text-2xl">${d.language === 'korean' ? '🇰🇷' : '🇬🇧'}</span>
          </div>
          <div class="flex gap-2 mt-4">
            <button class="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-3 py-2 text-xs font-medium transition-colors"
              onclick="startStudy('${d.id}', '${d.name}')">📖 Study</button>
            <button class="bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-3 py-2 text-xs transition-colors"
              onclick="addCardToDeck('${d.id}')">+ Card</button>
          </div>
        </div>`).join('');
    } catch (e) {
      toast.error('Failed to load decks: ' + e.message);
    }
  };

  await renderDecks();

  document.getElementById('add-deck-btn')?.addEventListener('click', () => {
    modal.form('New Deck', [
      { name: 'name', label: 'Deck Name', placeholder: 'e.g. Korean Basics' },
      { name: 'language', label: 'Language', type: 'select', value: 'english', options: [
        {value:'english',label:'🇬🇧 English'}, {value:'korean',label:'🇰🇷 Korean'}
      ]},
      { name: 'source_type', label: 'Source', type: 'select', value: 'manual', options: [
        {value:'manual',label:'Manual'}, {value:'youtube',label:'YouTube'}, {value:'upload',label:'Upload'}
      ]},
    ], async (data) => {
      try {
        await api.decks.create(data);
        toast.success('Deck created!');
        await renderDecks();
      } catch (e) { toast.error(e.message); }
    });
  });

  window.addCardToDeck = (deckId) => {
    modal.form('Add Flashcard', [
      { name: 'front', label: 'Front (Question/Word)', placeholder: 'Front side…' },
      { name: 'back', label: 'Back (Answer/Translation)', type: 'textarea', placeholder: 'Back side…' },
    ], async (data) => {
      try {
        await api.cards.create({ deck_id: deckId, front: data.front, back: data.back });
        toast.success('Card added!');
      } catch (e) { toast.error(e.message); }
    });
  };

  window.startStudy = async (deckId, deckName) => {
    try {
      const cards = await api.cards.review(deckId);
      if (cards.length === 0) {
        toast.info('No cards due for review! Great job! 🎉');
        return;
      }
      currentStudyDeck = deckId;
      currentDeckName = deckName;
      reviewCards = cards;
      reviewIndex = 0;
      cardFlipped = false;
      renderStudyMode(deckName);
    } catch (e) {
      toast.error('Failed to start study: ' + e.message);
    }
  };
}

function renderStudyMode(deckName) {
  const container = document.getElementById('study-mode');
  const list = document.getElementById('decks-list');
  if (!container || !list) return;

  list.classList.add('hidden');
  container.classList.remove('hidden');

  const card = reviewCards[reviewIndex];
  const progress = Math.round((reviewIndex / reviewCards.length) * 100);

  container.innerHTML = `
    <div class="max-w-2xl mx-auto">
      <div class="flex items-center justify-between mb-4">
        <button onclick="exitStudy()" class="text-gray-400 hover:text-white text-sm flex items-center gap-1">
          ← Back to Decks
        </button>
        <span class="text-sm text-gray-400">${reviewIndex + 1} / ${reviewCards.length}</span>
      </div>

      <!-- Progress bar -->
      <div class="w-full bg-gray-800 rounded-full h-2 mb-6">
        <div class="bg-indigo-600 h-2 rounded-full transition-all duration-500" style="width: ${progress}%"></div>
      </div>

      <!-- Flip card -->
      <div class="flip-card h-64 cursor-pointer mb-6 ${cardFlipped ? 'flipped' : ''}" id="flash-card" onclick="flipCard()">
        <div class="flip-card-inner rounded-2xl">
          <div class="flip-card-front bg-gray-900 border border-gray-700 rounded-2xl flex items-center justify-center p-8">
            <div class="text-center">
              <div class="text-xs text-gray-500 mb-3 uppercase tracking-wider">Question</div>
              <div class="text-2xl font-bold text-white">${card.front}</div>
              <div class="text-sm text-gray-500 mt-4">Click to reveal answer</div>
            </div>
          </div>
          <div class="flip-card-back bg-indigo-900/30 border border-indigo-700 rounded-2xl flex items-center justify-center p-8">
            <div class="text-center">
              <div class="text-xs text-indigo-400 mb-3 uppercase tracking-wider">Answer</div>
              <div class="text-2xl font-bold text-white">${card.back}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quality buttons (shown after flip) -->
      <div id="quality-btns" class="${cardFlipped ? '' : 'hidden'} grid grid-cols-3 gap-3">
        ${[
          {q:1, label:'Again', color:'bg-red-600 hover:bg-red-500'},
          {q:3, label:'Good',  color:'bg-yellow-600 hover:bg-yellow-500'},
          {q:5, label:'Easy',  color:'bg-green-600 hover:bg-green-500'},
        ].map(b => `
          <button onclick="submitReview(${b.q})"
            class="${b.color} text-white rounded-xl py-3 font-semibold text-sm transition-colors">
            ${b.label}
          </button>`).join('')}
      </div>

      ${!cardFlipped ? '<p class="text-center text-gray-500 text-sm mt-4">Flip the card to rate your recall</p>' : ''}
    </div>`;
}

window.flipCard = () => {
  cardFlipped = !cardFlipped;
  const card = document.getElementById('flash-card');
  const btns = document.getElementById('quality-btns');
  if (card) card.classList.toggle('flipped', cardFlipped);
  if (btns) btns.classList.toggle('hidden', !cardFlipped);
};

window.submitReview = async (quality) => {
  const card = reviewCards[reviewIndex];
  try {
    await api.cards.submit(card.id, quality);
    reviewIndex++;
    cardFlipped = false;
    if (reviewIndex >= reviewCards.length) {
      const container = document.getElementById('study-mode');
      container.innerHTML = `
        <div class="max-w-lg mx-auto text-center py-16">
          <div class="text-6xl mb-4">🎉</div>
          <h2 class="text-2xl font-bold text-white mb-2">Session Complete!</h2>
          <p class="text-gray-400 mb-6">You reviewed ${reviewCards.length} cards. Great work!</p>
          <button onclick="exitStudy()" class="bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl px-6 py-3 font-medium transition-colors">
            Back to Decks
          </button>
        </div>`;
    } else {
      renderStudyMode(currentDeckName);
    }
  } catch (e) {
    toast.error('Failed to submit review: ' + e.message);
  }
};

window.exitStudy = () => {
  const container = document.getElementById('study-mode');
  const list = document.getElementById('decks-list');
  if (container) container.classList.add('hidden');
  if (list) list.classList.remove('hidden');
  reviewCards = [];
  reviewIndex = 0;
};

window.pages = window.pages || {};
window.pages.flashcards = loadFlashcards;
