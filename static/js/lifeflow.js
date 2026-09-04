document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 6 seconds
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 6000);
});
