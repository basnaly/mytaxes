
document.addEventListener('DOMContentLoaded', function () {
    const message = document.querySelector('#message');
    if (message) {
        document.querySelector('#message').innerHTML;
        setTimeout(() => {
            document.querySelector('#message').innerHTML = "",
            window.location.replace(window.location.href);
        }, 3000)
    }
})