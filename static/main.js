function switchTab(tier, btn) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    // Update panels
    document.querySelectorAll('.room-class').forEach(p => p.classList.remove('active'));
    document.getElementById('room-' + tier).classList.add('active');
  }