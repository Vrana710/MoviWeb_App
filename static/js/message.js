// message.js

document.addEventListener('DOMContentLoaded', function () {
    // Automatic removal of success messages after a delay
    setTimeout(function () {
        const successMessages = document.querySelectorAll('.alert-success');
        successMessages.forEach(function (message) {
            message.style.opacity = 0;
            message.style.display = 'none';
        });
    }, 2000); // Adjust the timing (5000ms = 5 seconds) as needed
});
