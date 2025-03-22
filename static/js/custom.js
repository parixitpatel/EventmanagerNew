// custom.js

document.addEventListener('DOMContentLoaded', function() {
    // Select only the delete forms using the dedicated class.
    const deleteForms = document.querySelectorAll('form.delete-form');
  
    deleteForms.forEach(function(form) {
      form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent immediate form submission.
        // Show a single confirmation dialog.
        const confirmed = confirm("Are you sure you want to delete this event?");
        if (confirmed) {
          form.submit(); // Submit only if confirmed.
        }
      });
    });
  });
  