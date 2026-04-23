const form = document.querySelector('[data-assessment-form]');
const progressFill = document.getElementById('progressFill');
const answeredCount = document.getElementById('answeredCount');
const loaderOverlay = document.getElementById('loaderOverlay');

function updateScaleLabel(input) {
  const card = input.closest('[data-question-card]');
  const output = card ? card.querySelector('[data-scale-value]') : null;
  if (output) {
    output.textContent = input.value;
  }
}

function getAnsweredCount() {
  if (!form) {
    return 0;
  }

  const fields = Array.from(form.querySelectorAll('input[type="radio"], input[type="range"]'));
  const questionIds = new Set(fields.map((field) => field.name));
  let answered = 0;

  questionIds.forEach((name) => {
    if (form.querySelector(`[name="${name}"]:checked`) || form.querySelector(`[name="${name}"]`)) {
      answered += 1;
    }
  });

  return answered;
}

function updateProgress() {
  if (!form) {
    return;
  }

  const total = 25;
  const answered = getAnsweredCount();
  const percent = Math.min(100, (answered / total) * 100);

  if (progressFill) {
    progressFill.style.width = `${percent}%`;
  }

  if (answeredCount) {
    answeredCount.textContent = `${answered}/${total} answered`;
  }
}

if (form) {
  form.querySelectorAll('input[type="range"]').forEach((input) => {
    updateScaleLabel(input);
    input.addEventListener('input', () => {
      updateScaleLabel(input);
      updateProgress();
    });
  });

  form.querySelectorAll('input[type="radio"]').forEach((input) => {
    input.addEventListener('change', updateProgress);
  });

  form.addEventListener('submit', () => {
    if (loaderOverlay) {
      loaderOverlay.classList.add('active');
    }
  });

  updateProgress();
}