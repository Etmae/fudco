document.addEventListener('DOMContentLoaded', function () {
  const canvas = document.getElementById('dashRevenueChart');
  if (!canvas) return;

  function showChartNotice(message) {
    const note = document.createElement('p');
    note.className = 'text-xs text-slate-400 mt-2 text-center italic';
    note.textContent = message;
    canvas.parentNode.appendChild(note);
  }

  let labels, values;
  try {
    labels = JSON.parse(canvas.dataset.labels);
    values = JSON.parse(canvas.dataset.values);
  } catch (e) {
    console.error('Chart data parse error:', e);
    showChartNotice('Revenue chart data could not be loaded.');
    return;
  }

  if (!window.Chart) {
    showChartNotice('Revenue chart library could not be loaded.');
    return;
  }
  if (!Array.isArray(labels) || !Array.isArray(values)) {
    showChartNotice('Revenue chart data is not in the expected format.');
    return;
  }

  labels = labels.slice(0, values.length);
  values = values.map(v => Number(v) || 0);

  const maxVal = Math.max(...values);
  const hasData = values.some(v => v > 0);
  const suggestedMax = hasData ? maxVal * 1.3 : 50000;

  const barColors = values.map((_, i) =>
    i === values.length - 1 ? 'rgba(5,150,105,0.9)' : 'rgba(5,150,105,0.25)'
  );
  const borderColors = values.map((_, i) =>
    i === values.length - 1 ? 'rgba(5,150,105,1)' : 'rgba(5,150,105,0.6)'
  );

  const barLabelPlugin = {
    id: 'barLabels',
    afterDatasetDraw(chart) {
      const { ctx, data } = chart;
      ctx.save();
      chart.getDatasetMeta(0).data.forEach((bar, i) => {
        const val = data.datasets[0].data[i];
        if (val <= 0) return;
        ctx.fillStyle = '#475569';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        const lbl = val >= 1000 ? 'NGN ' + (val / 1000).toFixed(0) + 'k' : 'NGN ' + val;
        ctx.fillText(lbl, bar.x, bar.y - 3);
      });
      ctx.restore();
    }
  };

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Revenue',
        data: values,
        backgroundColor: barColors,
        borderColor: borderColors,
        borderWidth: 1.5,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    plugins: [barLabelPlugin],
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => 'NGN ' + Number(ctx.raw).toLocaleString('en-NG')
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax,
          grid: { color: 'rgba(0,0,0,0.04)' },
          ticks: {
            callback: v => v >= 1000 ? 'NGN ' + (v / 1000).toFixed(0) + 'k' : 'NGN ' + v,
            font: { size: 11 },
            maxTicksLimit: 5,
          }
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } }
        }
      }
    }
  });

  if (!hasData || (values.length === 1 && values[0] > 0)) {
    showChartNotice(hasData
      ? 'History builds as more days are recorded'
      : 'No sales yet - process a transaction to see revenue here.');
  }
});
