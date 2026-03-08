/**
 * Dashboard page.
 */
async function loadDashboard(container) {
  container.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <div class="text-3xl mb-2">✅</div>
        <div class="text-2xl font-bold text-white" id="dash-tasks-total">—</div>
        <div class="text-sm text-gray-400">Total Tasks</div>
      </div>
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <div class="text-3xl mb-2">🎯</div>
        <div class="text-2xl font-bold text-green-400" id="dash-tasks-completed">—</div>
        <div class="text-sm text-gray-400">Completed</div>
      </div>
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <div class="text-3xl mb-2">📚</div>
        <div class="text-2xl font-bold text-indigo-400" id="dash-words-week">—</div>
        <div class="text-sm text-gray-400">Words Learned (7d)</div>
      </div>
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <div class="text-3xl mb-2">📈</div>
        <div class="text-2xl font-bold text-purple-400" id="dash-completion-rate">—</div>
        <div class="text-sm text-gray-400">Completion Rate</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Upcoming deadlines -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-white">⏰ Upcoming Deadlines</h3>
          <button onclick="goToTasks()"
            class="text-xs text-indigo-400 hover:text-indigo-300">View all →</button>
        </div>
        <div id="dash-deadlines" class="space-y-3">
          <div class="text-gray-500 text-sm">Loading…</div>
        </div>
      </div>

      <!-- Quick add task -->
      <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
        <h3 class="font-semibold text-white mb-4">⚡ Quick Add Task</h3>
        <form id="quick-task-form" class="space-y-3">
          <input type="text" id="quick-task-title" placeholder="Task title…"
            class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <div class="flex gap-2">
            <select id="quick-task-priority"
              class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="high">🔴 High</option>
              <option value="medium" selected>🟡 Medium</option>
              <option value="low">🟢 Low</option>
            </select>
            <select id="quick-task-category"
              class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="work">💼 Work</option>
              <option value="study">📖 Study</option>
              <option value="learning">🧠 Learning</option>
              <option value="personal" selected>👤 Personal</option>
            </select>
          </div>
          <button type="submit"
            class="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors">
            + Add Task
          </button>
        </form>
      </div>
    </div>`;

  try {
    const data = await api.analytics.dashboard();
    document.getElementById('dash-tasks-total').textContent = data.tasks_total ?? '—';
    document.getElementById('dash-tasks-completed').textContent = data.tasks_completed ?? '—';
    document.getElementById('dash-words-week').textContent = data.words_learned_this_week ?? '—';
    document.getElementById('dash-completion-rate').textContent =
      data.completion_rate != null ? `${data.completion_rate}%` : '—';

    const deadlines = data.upcoming_deadlines || [];
    const dl = document.getElementById('dash-deadlines');
    if (deadlines.length === 0) {
      dl.innerHTML = '<p class="text-gray-500 text-sm">No upcoming deadlines 🎉</p>';
    } else {
      dl.innerHTML = deadlines.map(t => {
        const d = new Date(t.deadline);
        const priorityColor = { high: 'text-red-400', medium: 'text-yellow-400', low: 'text-green-400' };
        return `
          <div class="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
            <div>
              <div class="text-sm font-medium text-white">${t.title}</div>
              <div class="text-xs text-gray-400">${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</div>
            </div>
            <span class="text-xs font-medium ${priorityColor[t.priority] || 'text-gray-400'}">${t.priority}</span>
          </div>`;
      }).join('');
    }
  } catch (e) {
    toast.error('Failed to load dashboard: ' + e.message);
  }

  document.getElementById('quick-task-form')?.addEventListener('submit', async (e) => {    e.preventDefault();
    const title = document.getElementById('quick-task-title').value.trim();
    if (!title) return;
    try {
      await api.tasks.create({
        title,
        priority: document.getElementById('quick-task-priority').value,
        category: document.getElementById('quick-task-category').value,
      });
      toast.success('Task created!');
      document.getElementById('quick-task-title').value = '';
      loadDashboard(container);
    } catch (e) {
      toast.error('Failed to create task: ' + e.message);
    }
  });
}

window.pages = window.pages || {};
window.pages.dashboard = loadDashboard;

function goToTasks() {
  const tasksPage = document.getElementById('tasks-page');
  if (tasksPage) {
    document.querySelectorAll('.page').forEach(el => el.classList.add('hidden'));
    tasksPage.classList.remove('hidden');
    window.loadPage('tasks', tasksPage);
  }
}
