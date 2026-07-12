async function predict() {
  const btn = document.querySelector('.btn-predict');
  const btnText = document.getElementById('btn-text');
  const btnLoader = document.getElementById('btn-loader');

  const payload = {
    gender: document.getElementById('gender').value,
    married: document.getElementById('married').value,
    dependents: document.getElementById('dependents').value,
    education: document.getElementById('education').value,
    self_employed: document.getElementById('self_employed').value,
    property_area: document.getElementById('property_area').value,
    applicant_income: document.getElementById('applicant_income').value || 0,
    coapplicant_income: document.getElementById('coapplicant_income').value || 0,
    loan_amount: document.getElementById('loan_amount').value || 0,
    loan_term: document.getElementById('loan_term').value,
    credit_history: document.querySelector('input[name="credit_history"]:checked').value
  };

  if (!payload.applicant_income || !payload.loan_amount) {
    showError('Please fill in Applicant Income and Loan Amount.');
    return;
  }

  btnText.classList.add('hidden');
  btnLoader.classList.remove('hidden');
  btn.disabled = true;

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.error) {
      showError(data.error);
    } else {
      showResult(data);
    }
  } catch (err) {
    showError('Could not reach the server. Make sure the Flask app is running.');
  } finally {
    btnText.classList.remove('hidden');
    btnLoader.classList.add('hidden');
    btn.disabled = false;
  }
}

function showResult(data) {
  document.getElementById('result-placeholder')?.classList.add('hidden');
  document.querySelector('.result-placeholder').classList.add('hidden');
  document.getElementById('result-error').classList.add('hidden');
  document.getElementById('result-content').classList.remove('hidden');

  const icon = document.getElementById('result-icon');
  const title = document.getElementById('result-title');
  const msg = document.getElementById('result-msg');

  if (data.approved) {
    icon.textContent = '✓';
    icon.className = 'result-icon icon-approved';
    title.textContent = 'Loan Approved';
  } else {
    icon.textContent = '✕';
    icon.className = 'result-icon icon-rejected';
    title.textContent = 'Loan Not Approved';
  }
  msg.textContent = data.message || '';

  document.getElementById('confidence-bar').style.width = data.confidence + '%';
  document.getElementById('confidence-value').textContent = data.confidence + '%';
  document.getElementById('risk-level').textContent = data.risk_level;
  document.getElementById('model-used').textContent = data.model_used;
}

function showError(msg) {
  document.querySelector('.result-placeholder').classList.add('hidden');
  document.getElementById('result-content').classList.add('hidden');
  const errPanel = document.getElementById('result-error');
  errPanel.classList.remove('hidden');
  document.getElementById('error-msg').textContent = msg;
}

function resetForm() {
  document.getElementById('result-content').classList.add('hidden');
  document.getElementById('result-error').classList.add('hidden');
  document.querySelector('.result-placeholder').classList.remove('hidden');
  document.getElementById('applicant_income').value = '';
  document.getElementById('coapplicant_income').value = '';
  document.getElementById('loan_amount').value = '';
}

function setMode(mode) {
  const singleBtn = document.getElementById('btn-single-mode');
  const batchBtn = document.getElementById('btn-batch-mode');
  const singleForm = document.getElementById('single-form-container');
  const batchForm = document.getElementById('batch-form-container');
  const resultPanel = document.getElementById('result-panel');

  if (mode === 'single') {
    singleBtn.className = 'btn-primary';
    batchBtn.className = 'btn-secondary';
    singleForm.classList.remove('hidden');
    batchForm.classList.add('hidden');
    resultPanel.style.display = 'flex';
  } else {
    singleBtn.className = 'btn-secondary';
    batchBtn.className = 'btn-primary';
    singleForm.classList.add('hidden');
    batchForm.classList.remove('hidden');
    resultPanel.style.display = 'none';
  }
}

async function batchPredict() {
  const fileInput = document.getElementById('batch_file');
  const btn = document.querySelector('#batch-form-container .btn-predict');
  const btnText = document.getElementById('btn-batch-text');
  const btnLoader = document.getElementById('btn-batch-loader');

  if (!fileInput.files || fileInput.files.length === 0) {
    alert('Please select a CSV file first.');
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  btnText.classList.add('hidden');
  btnLoader.classList.remove('hidden');
  btn.disabled = true;

  try {
    const res = await fetch('/api/batch_predict', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const errorData = await res.json();
      alert('Error: ' + (errorData.error || 'Something went wrong.'));
    } else {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'batch_predictions.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }
  } catch (err) {
    alert('Could not reach the server.');
  } finally {
    btnText.classList.remove('hidden');
    btnLoader.classList.add('hidden');
    btn.disabled = false;
  }
}

