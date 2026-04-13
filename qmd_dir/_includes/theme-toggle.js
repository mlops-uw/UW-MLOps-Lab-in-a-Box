<script>
(function() {
  // Theme toggle functionality
  const toggle = document.getElementById('theme-toggle');
  const html = document.documentElement;
  
  // Icons for light and dark mode
  const sunIcon = '☀️';
  const moonIcon = '🌙';
  
  // Get saved theme or default to dark
  const savedTheme = localStorage.getItem('theme') || 'dark';
  html.setAttribute('data-bs-theme', savedTheme);
  
  // Update button icon
  function updateIcon() {
    const currentTheme = html.getAttribute('data-bs-theme');
    if (toggle) {
      toggle.textContent = currentTheme === 'dark' ? sunIcon : moonIcon;
      toggle.setAttribute('aria-label', `Switch to ${currentTheme === 'dark' ? 'light' : 'dark'} mode`);
    }
  }
  
  updateIcon();
  
  // Toggle theme on button click
  if (toggle) {
    toggle.addEventListener('click', function() {
      const currentTheme = html.getAttribute('data-bs-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      html.setAttribute('data-bs-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateIcon();
    });
  }
})();
</script>
