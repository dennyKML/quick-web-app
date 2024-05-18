document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('#flash-messages div');
    flashMessages.forEach(messageDiv => {
        const category = messageDiv.getAttribute('data-category');
        const message = messageDiv.getAttribute('data-message');
        if (category && message) {
          alert(message);
        }
    });
});