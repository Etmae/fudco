document.addEventListener('DOMContentLoaded', function () {
  const canvas = document.getElementById('revenueChart');
  if (!canvas) return;

  let labels, values;
  try {
    labels = JSON.parse(canvas.dataset.labels);
    values = JSON.parse(canvas.dataset.values);
  } catch (e) { return; }

  if (!window.Chart || !Array.isArray(labels) || !Array.isArray(values)) return;
  labels = labels.slice(0, values.length);
  values = values.map(v => Number(v) || 0);

  const maxVal       = Math.max(...values);
  const suggestedMax = maxVal > 0 ? maxVal * 1.3 : 50000;

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Revenue (₦)',
        data: values,
        backgroundColor: 'rgba(16,185,129,0.2)',
        borderColor: 'rgba(16,185,129,1)',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => '₦' + Number(ctx.raw).toLocaleString('en-NG')
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          suggestedMax,
          grid: { color: 'rgba(0,0,0,0.04)' },
          ticks: {
            callback: v => v >= 1000 ? '₦' + (v/1000).toFixed(0) + 'k' : '₦' + v,
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
});
