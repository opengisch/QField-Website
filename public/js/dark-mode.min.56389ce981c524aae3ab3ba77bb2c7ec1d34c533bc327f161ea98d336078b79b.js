    (function() {
      const icon = document.getElementById('themeIcon');
      const btn  = document.getElementById('themeToggle');

      function renderIcon() {
        const t = document.documentElement.getAttribute('data-bs-theme');
        icon.className = t === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
      }

      function setTheme(next) {
        document.documentElement.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        renderIcon();
      }

      btn?.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
        setTheme(current === 'dark' ? 'light' : 'dark');
      });

      renderIcon();
    })();