// main.js
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('mealTypeSelect').addEventListener('change', function() {
        document.getElementById('filterForm').submit();
    });
});
