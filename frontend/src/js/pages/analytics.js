/**
 * Analytics page with Plotly charts.
 */
async function loadAnalytics(container) {
  container.innerHTML = `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 class="font-semibold text-white mb-4">📈 Task Completion Over Time</h3>
        <div id="chart-completion" class="h-64"></div>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 class="font-semibold text-white mb-4">🗂 Category Breakdown</h3>
        <div id="chart-category" class="h-64"></div>
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 class="font-semibold text-white mb-4">📚 Vocabulary Growth</h3>
        <div id="chart-vocab" class="h-64"></div>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h3 class="font-semibold text-white mb-4">🤖 ML Recommendations</h3>
        <div id="recommendations-card" class="space-y-3">
          <div class="text-gray-500 text-sm">Loading…</div>
        </div>
      </div>
    </div>`;

  const plotLayout = (title) => ({
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#9ca3af', size: 11 },
    title: { text: '', font: { color: '#fff' } },
    margin: { t: 10, r: 10, b: 40, l: 40 },
    xaxis: { gridcolor: '#374151', zerolinecolor: '#374151' },
    yaxis: { gridcolor: '#374151', zerolinecolor: '#374151' },
  });

  try {
    const [prodData, recommendations] = await Promise.all([
      api.analytics.productivity(),
      api.analytics.recommendations(),
    ]);

    // Completion rate over time
    const completionChart = prodData.analysis?.completion_chart || [];
    if (completionChart.length > 0) {
      Plotly.newPlot('chart-completion', [{
        x: completionChart.map(d => d.date),
        y: completionChart.map(d => d.rate * 100),
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#4f46e5', width: 2 },
        marker: { color: '#4f46e5', size: 5 },
        name: 'Completion %',
      }], { ...plotLayout(), yaxis: { ...plotLayout().yaxis, range: [0, 100], ticksuffix: '%' } },
      { displayModeBar: false, responsive: true });
    } else {
      document.getElementById('chart-completion').innerHTML = '<div class="flex items-center justify-center h-full text-gray-500 text-sm">No data yet. Complete some tasks to see trends!</div>';
    }

    // Category breakdown pie chart
    const categoryChart = prodData.analysis?.category_chart || {};
    const catLabels = Object.keys(categoryChart);
    if (catLabels.length > 0) {
      Plotly.newPlot('chart-category', [{
        labels: catLabels,
        values: Object.values(categoryChart),
        type: 'pie',
        hole: 0.4,
        marker: { colors: ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b'] },
        textinfo: 'label+percent',
        textfont: { color: '#fff' },
      }], { ...plotLayout(), showlegend: false }, { displayModeBar: false, responsive: true });
    } else {
      document.getElementById('chart-category').innerHTML = '<div class="flex items-center justify-center h-full text-gray-500 text-sm">No category data yet.</div>';
    }

    // Vocabulary growth
    const langData = await api.analytics.language().catch(() => ({ records: [], vocabulary_summary: {} }));
    const vocabSummary = langData.vocabulary_summary || {};
    if (Object.keys(vocabSummary).length > 0) {
      Plotly.newPlot('chart-vocab', [{
        x: Object.keys(vocabSummary),
        y: Object.values(vocabSummary).map(v => v.total || 0),
        type: 'bar',
        marker: { color: ['#4f46e5', '#06b6d4', '#10b981'] },
        name: 'Total Words',
      }, {
        x: Object.keys(vocabSummary),
        y: Object.values(vocabSummary).map(v => v.learned || 0),
        type: 'bar',
        marker: { color: ['#6366f1', '#22d3ee', '#34d399'] },
        name: 'Learned',
      }], { ...plotLayout(), barmode: 'group' }, { displayModeBar: false, responsive: true });
    } else {
      document.getElementById('chart-vocab').innerHTML = '<div class="flex items-center justify-center h-full text-gray-500 text-sm">No vocabulary data yet.</div>';
    }

    // Recommendations
    const recCard = document.getElementById('recommendations-card');
    const suggestions = recommendations.suggestions || [];
    if (suggestions.length > 0) {
      recCard.innerHTML = `
        <div class="space-y-2">
          ${suggestions.map(s => `
            <div class="flex items-start gap-2 p-3 bg-gray-800 rounded-lg">
              <span class="text-indigo-400 mt-0.5">💡</span>
              <p class="text-sm text-gray-300">${s}</p>
            </div>`).join('')}
        </div>
        <div class="mt-4 pt-4 border-t border-gray-800 grid grid-cols-2 gap-3 text-sm">
          <div class="bg-gray-800 rounded-lg p-3">
            <div class="text-gray-500 text-xs mb-1">Best Day</div>
            <div class="font-medium text-white">${recommendations.best_day || '—'}</div>
          </div>
          <div class="bg-gray-800 rounded-lg p-3">
            <div class="text-gray-500 text-xs mb-1">Top Category</div>
            <div class="font-medium text-white">${recommendations.top_category || '—'}</div>
          </div>
        </div>`;
    } else {
      recCard.innerHTML = '<p class="text-gray-500 text-sm">Complete more tasks to get ML-powered recommendations!</p>';
    }
  } catch (e) {
    toast.error('Failed to load analytics: ' + e.message);
  }
}

window.pages = window.pages || {};
window.pages.analytics = loadAnalytics;
