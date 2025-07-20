document.addEventListener('DOMContentLoaded', function() {
  console.log("Filter state:", {
    year: new URLSearchParams(window.location.search).get('year'),
    month: new URLSearchParams(window.location.search).get('month'),
    category: new URLSearchParams(window.location.search).get('category')
  });

  const filterForm = document.getElementById('filter-form');
  if (filterForm) {
    filterForm.addEventListener('change', function(e) {
      const formData = new FormData(this);
      console.log("Filter changed:", {
        year: formData.get('year'),
        month: formData.get('month'),
        category: formData.get('category')
      });
    });
  }
});

