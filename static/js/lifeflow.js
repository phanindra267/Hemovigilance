(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {

    // 1. Auto-dismiss flash alerts smoothly after 6s
    setTimeout(function() {
      document.querySelectorAll('.alert-dismissible').forEach(function(el) {
        try {
          var bsAlert = new bootstrap.Alert(el);
          bsAlert.close();
        } catch(e) {}
      });
    }, 6000);

    // 2. Active sidebar link detection based on current URL path
    var currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar .nav-link').forEach(function(link) {
      var href = link.getAttribute('href');
      if (href && href !== '/' && currentPath.startsWith(href)) {
        link.classList.add('active');
      } else if (href === '/' && currentPath === '/') {
        link.classList.add('active');
      }
    });

    // 3. Mobile sidebar toggle
    var toggleBtn = document.getElementById('sidebarToggle');
    var sidebar = document.querySelector('.sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (toggleBtn && sidebar) {
      toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('d-none');
        sidebar.classList.toggle('d-flex');
        sidebar.style.position = 'fixed';
        sidebar.style.left = '0';
        sidebar.style.top = 'var(--navbar-h)';
        sidebar.style.zIndex = '1020';
        if (overlay) overlay.classList.toggle('d-none');
      });
    }
    if (overlay) {
      overlay.addEventListener('click', function() {
        if (sidebar) {
          sidebar.classList.add('d-none');
          sidebar.classList.remove('d-flex');
        }
        overlay.classList.add('d-none');
      });
    }

    // 4. Confirm destructive / critical clinical actions
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
      el.addEventListener('click', function(e) {
        var msg = el.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
        if (!window.confirm(msg)) {
          e.preventDefault();
        }
      });
    });

    // 5. Enhance Django form inputs with Bootstrap styling automatically
    document.querySelectorAll('form input, form select, form textarea').forEach(function(el) {
      if (!el.classList.contains('btn') && !el.classList.contains('form-check-input')) {
        if (el.type !== 'checkbox' && el.type !== 'radio' && el.type !== 'submit' && el.type !== 'button' && el.type !== 'hidden') {
          if (el.tagName === 'SELECT') {
            if (!el.classList.contains('form-select')) el.classList.add('form-select');
          } else {
            if (!el.classList.contains('form-control')) el.classList.add('form-control');
          }
        }
      }
    });

    // 6. Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
      try {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      } catch(e) {}
    });

  });
})();
