document.addEventListener('DOMContentLoaded', () => {
    const loginWrapper = document.querySelector('.login-wrapper');
    const signupWrapper = document.querySelector('.signup-wrapper');
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    const authContainer = document.querySelector('.auth-container');

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');

            if (target === 'signup') {
                loginWrapper.classList.remove('active');
                loginWrapper.classList.add('inactive-left');

                signupWrapper.classList.remove('inactive-left');
                setTimeout(() => {
                    signupWrapper.classList.add('active');
                    authContainer.style.minHeight = '580px';
                }, 50);
            } else {
                signupWrapper.classList.remove('active');

                loginWrapper.classList.remove('inactive-left');
                setTimeout(() => {
                    loginWrapper.classList.add('active');
                    authContainer.style.minHeight = '480px';
                }, 50);
            }
        });
    });

    const scrollBtn = document.querySelector('.scroll-btn');
    const scrollIndicator = document.querySelector('.scroll-indicator');

    // Fallback for browsers that don't suppport CSS smooth scroll perfectly
    const scrollToAuth = (e) => {
        e.preventDefault();
        const authSection = document.getElementById('auth-section');
        authSection.scrollIntoView({ behavior: 'smooth' });
    };

    if (scrollBtn) scrollBtn.addEventListener('click', scrollToAuth);
    if (scrollIndicator) scrollIndicator.addEventListener('click', scrollToAuth);
});
