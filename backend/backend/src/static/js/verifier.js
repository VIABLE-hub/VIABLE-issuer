/**
 * Verifier.js - Wissenschaftlich sauberes Status-Update ohne Frontend-Framework
 * Designed by HERZCHIRURG
 */

/**
 * Updates the status icon of a verification step
 * 
 * @param {string} id - ID of the element to update
 * @param {string} status - Status ('pending', 'success', or 'fail')
 */
function updateStatus(id, status) {
  const el = document.getElementById(id);
  if (!el) return;

  if (status === 'pending') {
    el.textContent = '⏳';
    el.className = 'text-yellow-600';
  } else if (status === 'success') {
    el.textContent = '✅';
    el.className = 'text-green-600';
  } else if (status === 'fail') {
    el.textContent = '❌';
    el.className = 'text-red-600';
  }
}

/**
 * Toggles the visibility of technical details
 */
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.toggle-tech-details').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.target;
      document.getElementById(id).classList.toggle('hidden');
    });
  });
}); 