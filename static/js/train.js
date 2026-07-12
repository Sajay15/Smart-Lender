async function trainModel() {
  const btn = document.getElementById('train-btn');
  const log = document.getElementById('output-log');
  const badge = document.getElementById('train-status-badge');
  const vizSection = document.getElementById('viz-section');

  btn.disabled = true;
  btn.textContent = 'Training in progress…';
  badge.textContent = 'Running';
  badge.className = 'status-badge status-running';
  log.innerHTML = '<span style="color:#818CF8">$ python train_model.py</span>\n\nStarting training pipeline...\nThis may take 30–90 seconds depending on your machine.\n';

  try {
    const res = await fetch('/api/train', { method: 'POST' });
    const data = await res.json();

    if (data.success) {
      badge.textContent = 'Success';
      badge.className = 'status-badge status-success';
      log.textContent = data.output || 'Training complete.';
      vizSection.classList.remove('hidden');

      // Cache-bust images
      document.querySelectorAll('.viz-item img').forEach(img => {
        const src = img.src.split('?')[0];
        img.src = src + '?t=' + Date.now();
        img.style.display = 'block';
      });
    } else {
      badge.textContent = 'Error';
      badge.className = 'status-badge status-error';
      log.textContent = 'Error:\n' + data.message;
    }
  } catch (err) {
    badge.textContent = 'Error';
    badge.className = 'status-badge status-error';
    log.textContent = 'Could not reach the server.\n' + err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Start Training Pipeline';
  }
}
