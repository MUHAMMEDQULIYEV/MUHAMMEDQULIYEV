/**
 * Tasks page — Kanban board.
 */
async function loadTasks(container) {
  container.innerHTML = `
    <!-- Filter bar -->
    <div class="flex flex-wrap gap-3 mb-6">
      <select id="filter-status" class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
        <option value="">All Status</option>
        <option value="not_started">Not Started</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
        <option value="archived">Archived</option>
      </select>
      <select id="filter-category" class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
        <option value="">All Categories</option>
        <option value="work">Work</option>
        <option value="study">Study</option>
        <option value="learning">Learning</option>
        <option value="personal">Personal</option>
      </select>
      <select id="filter-priority" class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
        <option value="">All Priorities</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>
      <button id="apply-filters"
        class="bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors">
        Filter
      </button>
      <button id="add-task-btn"
        class="ml-auto bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors">
        + New Task
      </button>
    </div>

    <!-- Kanban board -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4" id="kanban-board">
      ${['not_started','in_progress','completed','archived'].map(s => `
        <div class="bg-gray-900 rounded-xl border border-gray-800 kanban-col">
          <div class="px-4 py-3 border-b border-gray-800 font-semibold text-sm text-gray-300">
            ${{not_started:'⬜ Not Started', in_progress:'🔵 In Progress', completed:'✅ Completed', archived:'📦 Archived'}[s]}
          </div>
          <div class="p-3 space-y-3 min-h-40" id="col-${s}">
            <div class="text-gray-600 text-sm text-center py-4">Loading…</div>
          </div>
        </div>`).join('')}
    </div>`;

  const fetchTasks = async () => {
    const status = document.getElementById('filter-status').value;
    const category = document.getElementById('filter-category').value;
    const priority = document.getElementById('filter-priority').value;
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (category) params.append('category', category);
    if (priority) params.append('priority', priority);
    const qs = params.toString() ? `?${params}` : '';
    return api.tasks.list(qs);
  };

  const renderTasks = async () => {
    try {
      const tasks = await fetchTasks();
      state.set('tasks', tasks);

      const cols = { not_started: [], in_progress: [], completed: [], archived: [] };
      tasks.forEach(t => { if (cols[t.status]) cols[t.status].push(t); });

      Object.entries(cols).forEach(([status, items]) => {
        const col = document.getElementById(`col-${status}`);
        if (!col) return;
        if (items.length === 0) {
          col.innerHTML = '<div class="text-gray-600 text-sm text-center py-4">Empty</div>';
          return;
        }
        col.innerHTML = items.map(t => {
          const prioClasses = { high: 'badge-high', medium: 'badge-medium', low: 'badge-low' };
          const deadline = t.deadline ? new Date(t.deadline).toLocaleDateString() : '';
          return `
            <div class="bg-gray-800 rounded-lg p-3 border border-gray-700 hover:border-indigo-500 transition-colors group">
              <div class="flex items-start justify-between gap-2 mb-2">
                <div class="text-sm font-medium text-white flex-1">${t.title}</div>
                <span class="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ${prioClasses[t.priority]}">${t.priority}</span>
              </div>
              ${t.description ? `<div class="text-xs text-gray-400 mb-2 line-clamp-2">${t.description}</div>` : ''}
              <div class="flex items-center justify-between">
                <span class="text-xs text-gray-500">${t.category}</span>
                ${deadline ? `<span class="text-xs text-gray-500">📅 ${deadline}</span>` : ''}
              </div>
              <div class="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button class="text-xs text-indigo-400 hover:text-indigo-300" onclick="editTask('${t.id}')">Edit</button>
                <button class="text-xs text-red-400 hover:text-red-300" onclick="deleteTask('${t.id}')">Delete</button>
                ${t.status !== 'completed' ? `<button class="text-xs text-green-400 hover:text-green-300 ml-auto" onclick="completeTask('${t.id}')">✓ Done</button>` : ''}
              </div>
            </div>`;
        }).join('');
      });
    } catch (e) {
      toast.error('Failed to load tasks: ' + e.message);
    }
  };

  await renderTasks();

  document.getElementById('apply-filters')?.addEventListener('click', renderTasks);

  document.getElementById('add-task-btn')?.addEventListener('click', () => {
    modal.form('New Task', [
      { name: 'title', label: 'Title', placeholder: 'Task title…' },
      { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Optional description…' },
      { name: 'category', label: 'Category', type: 'select', value: 'personal', options: [
        {value:'work',label:'💼 Work'}, {value:'study',label:'📖 Study'},
        {value:'learning',label:'🧠 Learning'}, {value:'personal',label:'👤 Personal'}
      ]},
      { name: 'priority', label: 'Priority', type: 'select', value: 'medium', options: [
        {value:'high',label:'🔴 High'}, {value:'medium',label:'🟡 Medium'}, {value:'low',label:'🟢 Low'}
      ]},
      { name: 'deadline', label: 'Deadline', type: 'datetime-local' },
      { name: 'estimated_duration', label: 'Estimated Duration (minutes)', type: 'number', placeholder: '60' },
    ], async (data) => {
      try {
        const payload = { title: data.title, description: data.description || null,
          category: data.category, priority: data.priority,
          deadline: data.deadline ? new Date(data.deadline).toISOString() : null,
          estimated_duration: data.estimated_duration ? parseInt(data.estimated_duration) : null,
        };
        await api.tasks.create(payload);
        toast.success('Task created!');
        await renderTasks();
      } catch (e) { toast.error(e.message); }
    });
  });

  window.editTask = async (id) => {
    const task = state.tasks.find(t => t.id === id);
    if (!task) return;
    const deadline = task.deadline ? new Date(task.deadline).toISOString().slice(0, 16) : '';
    modal.form('Edit Task', [
      { name: 'title', label: 'Title', value: task.title },
      { name: 'description', label: 'Description', type: 'textarea', value: task.description || '' },
      { name: 'category', label: 'Category', type: 'select', value: task.category, options: [
        {value:'work',label:'💼 Work'}, {value:'study',label:'📖 Study'},
        {value:'learning',label:'🧠 Learning'}, {value:'personal',label:'👤 Personal'}
      ]},
      { name: 'priority', label: 'Priority', type: 'select', value: task.priority, options: [
        {value:'high',label:'🔴 High'}, {value:'medium',label:'🟡 Medium'}, {value:'low',label:'🟢 Low'}
      ]},
      { name: 'status', label: 'Status', type: 'select', value: task.status, options: [
        {value:'not_started',label:'⬜ Not Started'}, {value:'in_progress',label:'🔵 In Progress'},
        {value:'completed',label:'✅ Completed'}, {value:'archived',label:'📦 Archived'}
      ]},
      { name: 'deadline', label: 'Deadline', type: 'datetime-local', value: deadline },
    ], async (data) => {
      try {
        await api.tasks.update(id, {
          title: data.title, description: data.description || null,
          category: data.category, priority: data.priority, status: data.status,
          deadline: data.deadline ? new Date(data.deadline).toISOString() : null,
        });
        toast.success('Task updated!');
        await renderTasks();
      } catch (e) { toast.error(e.message); }
    });
  };

  window.deleteTask = async (id) => {
    if (!confirm('Delete this task?')) return;
    try {
      await api.tasks.remove(id);
      toast.success('Task deleted.');
      await renderTasks();
    } catch (e) { toast.error(e.message); }
  };

  window.completeTask = async (id) => {
    try {
      await api.tasks.update(id, { status: 'completed' });
      toast.success('Task completed! 🎉');
      await renderTasks();
    } catch (e) { toast.error(e.message); }
  };
}

window.pages = window.pages || {};
window.pages.tasks = loadTasks;
