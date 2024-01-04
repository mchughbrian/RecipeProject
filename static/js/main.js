// main.js
document.addEventListener('DOMContentLoaded', function() {
    var mealTypeSelect = document.getElementById('mealTypeSelect');
    if (mealTypeSelect) {
        mealTypeSelect.addEventListener('change', function() {
            document.getElementById('filterForm').submit();
        });
    }
});
