// Hybrid Trader Custom Scripts

// Add copy button to code blocks
document.addEventListener('DOMContentLoaded', function() {
  // Add smooth scroll behavior
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });

  // Add animation to cards on scroll
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animation = 'fadeInUp 0.6s ease-out';
      }
    });
  }, {
    threshold: 0.1
  });

  document.querySelectorAll('.grid.cards > *').forEach(card => {
    observer.observe(card);
  });

  // Search analytics (optional)
  const searchInput = document.querySelector('[data-md-component="search-query"]');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      // Track searches if needed
      console.log('Search query:', this.value);
    });
  }
});

// Add animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animated {
    animation: fadeInUp 0.6s ease-out;
  }
`;
document.head.appendChild(style);

// Utility function for tracking
window.hybridTraderAnalytics = {
  trackEvent: function(category, action, label) {
    console.log(`Event: ${category} > ${action}`, label);
    // Integrate with analytics service if needed
  },
  trackPageView: function(path) {
    console.log(`Page view: ${path}`);
  }
};
