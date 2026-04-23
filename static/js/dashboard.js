const profileNode = document.getElementById('profile-data');

if (profileNode && window.Chart) {
  const profile = JSON.parse(profileNode.textContent);
  const scores = profile.scores;

  const radarCanvas = document.getElementById('radarChart');
  if (radarCanvas) {
    new Chart(radarCanvas, {
      type: 'radar',
      data: {
        labels: ['Extroversion', 'Risk', 'Logic', 'Planning'],
        datasets: [{
          label: 'Your Digital Twin',
          data: [
            scores.introversion_extroversion,
            scores.risk_level,
            scores.logical_emotional,
            scores.planning_spontaneity,
          ],
          borderColor: '#54f0ff',
          backgroundColor: 'rgba(84, 240, 255, 0.18)',
          pointBackgroundColor: '#8f6dff',
          borderWidth: 2,
          pointRadius: 4,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: '#edf3ff' } },
        },
        scales: {
          r: {
            angleLines: { color: 'rgba(255,255,255,0.12)' },
            grid: { color: 'rgba(255,255,255,0.1)' },
            pointLabels: { color: '#edf3ff', font: { size: 12 } },
            ticks: { display: false, backdropColor: 'transparent', color: '#9fb0d0' },
            suggestedMin: 0,
            suggestedMax: 100,
          },
        },
      },
    });
  }

  const barCanvas = document.getElementById('barChart');
  if (barCanvas) {
    new Chart(barCanvas, {
      type: 'bar',
      data: {
        labels: ['Extroversion', 'Risk', 'Logic', 'Planning'],
        datasets: [{
          label: 'Score',
          data: [
            scores.introversion_extroversion,
            scores.risk_level,
            scores.logical_emotional,
            scores.planning_spontaneity,
          ],
          borderRadius: 14,
          backgroundColor: ['#54f0ff', '#8f6dff', '#4e8dff', '#ff6bd6'],
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: {
            ticks: { color: '#edf3ff' },
            grid: { display: false },
          },
          y: {
            min: 0,
            max: 100,
            ticks: { color: '#9fb0d0' },
            grid: { color: 'rgba(255,255,255,0.1)' },
          },
        },
      },
    });
  }
}