document.addEventListener('DOMContentLoaded', function () {
    var toggleDarkModeButton = document.getElementById('toggleDarkMode');
    toggleDarkModeButton.addEventListener('click', function () {
        var htmlElement = document.documentElement;
        if (htmlElement.getAttribute('data-bs-theme') === 'dark') {
            htmlElement.setAttribute('data-bs-theme', 'light');
        } else {
            htmlElement.setAttribute('data-bs-theme', 'dark');
        }
    });
});
