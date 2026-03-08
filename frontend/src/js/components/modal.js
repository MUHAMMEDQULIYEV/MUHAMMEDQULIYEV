/**
 * Modal component.
 */
const modal = {
  show(title, contentHTML, onConfirm = null) {
    const container = document.getElementById('modal-container');
    container.innerHTML = `
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60" id="modal-overlay">
        <div class="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-700">
            <h2 class="text-lg font-semibold text-white">${title}</h2>
            <button onclick="modal.close()" class="text-gray-400 hover:text-white text-xl leading-none">&times;</button>
          </div>
          <div class="px-6 py-4">
            ${contentHTML}
          </div>
          ${onConfirm ? `
          <div class="px-6 py-4 border-t border-gray-700 flex justify-end gap-3">
            <button onclick="modal.close()" class="px-4 py-2 rounded-lg bg-gray-700 text-gray-300 hover:bg-gray-600 text-sm">Cancel</button>
            <button id="modal-confirm-btn" class="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 text-sm font-medium">Confirm</button>
          </div>` : ''}
        </div>
      </div>`;

    if (onConfirm) {
      document.getElementById('modal-confirm-btn').addEventListener('click', async () => {
        await onConfirm();
        modal.close();
      });
    }

    document.getElementById('modal-overlay').addEventListener('click', (e) => {
      if (e.target.id === 'modal-overlay') modal.close();
    });
  },

  close() {
    const container = document.getElementById('modal-container');
    container.innerHTML = '';
  },

  form(title, fields, onSubmit) {
    const fieldsHTML = fields.map(f => `
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-300 mb-1">${f.label}</label>
        ${f.type === 'textarea'
          ? `<textarea id="mf_${f.name}" rows="4" placeholder="${f.placeholder || ''}" class="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">${f.value || ''}</textarea>`
          : f.type === 'select'
          ? `<select id="mf_${f.name}" class="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
               ${f.options.map(o => `<option value="${o.value}" ${f.value === o.value ? 'selected' : ''}>${o.label}</option>`).join('')}
             </select>`
          : `<input id="mf_${f.name}" type="${f.type || 'text'}" value="${f.value || ''}" placeholder="${f.placeholder || ''}" class="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />`
        }
      </div>`).join('');

    modal.show(title, `<form id="modal-form" class="space-y-1">${fieldsHTML}</form>`, async () => {
      const data = {};
      fields.forEach(f => {
        const el = document.getElementById(`mf_${f.name}`);
        data[f.name] = el ? el.value : '';
      });
      await onSubmit(data);
    });
  },
};

window.modal = modal;
