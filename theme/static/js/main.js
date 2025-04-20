document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const body = document.body;

    if (sidebarToggleBtn && sidebar) {
        // Toggle sidebar on mobile
        sidebarToggleBtn.addEventListener('click', () => {
            // Only apply transformations on mobile
            if (window.innerWidth < 1024) { // Changed from 768 to 1024 (lg breakpoint)
                sidebar.classList.toggle('mobile-visible');
                sidebarOverlay.classList.toggle('hidden');
                body.classList.toggle('overflow-hidden');
            }
        });
    }

    // Close sidebar when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('mobile-visible');
            sidebarOverlay.classList.add('hidden');
            body.classList.remove('overflow-hidden');
        });
    }

    // Close sidebar when clicking a link (on mobile)
    document.querySelectorAll('#sidebar a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 1024) { // Changed from 768 to 1024 (lg breakpoint)
                sidebar.classList.remove('mobile-visible');
                sidebarOverlay.classList.add('hidden');
                body.classList.remove('overflow-hidden');
            }
        });
    });

    // Handle responsive behavior when resizing
    window.addEventListener('resize', () => {
        if (window.innerWidth >= 1024) { // Changed from 768 to 1024 (lg breakpoint)
            // Desktop behavior
            sidebar.classList.remove('mobile-visible');
            sidebarOverlay.classList.add('hidden');
            body.classList.remove('overflow-hidden');
        } else {
            // Mobile behavior - ensure sidebar is hidden unless explicitly shown
            if (!sidebar.classList.contains('mobile-visible')) {
                sidebar.classList.remove('mobile-visible');
            }
        }
    });

    // User menu functionality
    const userMenuButton = document.getElementById('user-menu-btn');
    const userMenu = document.getElementById('user-menu');

    if (userMenuButton && userMenu) {
        // Toggle user menu
        userMenuButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event from bubbling to document
            const isExpanded = userMenuButton.getAttribute('aria-expanded') === 'true';
            userMenuButton.setAttribute('aria-expanded', !isExpanded);
            userMenu.classList.toggle('hidden');
        });

        // Close user menu when clicking outside
        document.addEventListener('click', (event) => {
            if (userMenu && !userMenu.contains(event.target) && !userMenuButton.contains(event.target)) {
                userMenu.classList.add('hidden');
                userMenuButton.setAttribute('aria-expanded', 'false');
            }
        });

        // Close user menu when pressing Escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && userMenu && !userMenu.classList.contains('hidden')) {
                userMenu.classList.add('hidden');
                userMenuButton.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const strengthIndicator = this.nextElementSibling;
            if (strengthIndicator && strengthIndicator.classList.contains('password-strength')) {
                const password = this.value;
                let strength = 0;
                
                // Length check
                if (password.length >= 8) strength++;
                if (password.length >= 12) strength++;
                
                // Character type checks
                if (/[A-Z]/.test(password)) strength++;
                if (/[0-9]/.test(password)) strength++;
                if (/[^A-Za-z0-9]/.test(password)) strength++;
                
                // Update indicator
                strengthIndicator.innerHTML = '';
                for (let i = 0; i < 5; i++) {
                    const segment = document.createElement('div');
                    segment.className = 'h-1 rounded';
                    segment.style.width = '20%';
                    segment.style.marginRight = '2px';
                    segment.style.display = 'inline-block';
                    segment.style.backgroundColor = i < strength ? 
                        (strength < 3 ? 'red' : strength < 5 ? 'orange' : 'green') : '#e5e7eb';
                    strengthIndicator.appendChild(segment);
                }
                
                // Text description
                const text = document.createElement('span');
                text.className = 'text-xs ml-2';
                if (strength === 0) {
                    text.textContent = 'Very weak';
                    text.className += ' text-red-500';
                } else if (strength < 3) {
                    text.textContent = 'Weak';
                    text.className += ' text-orange-500';
                } else if (strength < 5) {
                    text.textContent = 'Good';
                    text.className += ' text-blue-500';
                } else {
                    text.textContent = 'Strong';
                    text.className += ' text-green-500';
                }
                strengthIndicator.appendChild(text);
            }
        });
    });
    
    // Auto-dismiss messages after 5 seconds
    const messages = document.querySelectorAll('[role="alert"]');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
});