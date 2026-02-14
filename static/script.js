document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function (event) {
            // Check if form is valid (if using browser validation)
            if (!form.checkValidity()) {
                // If form is invalid, browser shows error, don't show loading
                return;
            }

            const submitBtn = form.querySelector('button[type="submit"]');

            if (submitBtn) {
                // Prevent double submission
                if (submitBtn.classList.contains('loading')) {
                    event.preventDefault();
                    return;
                }

                // Add loading class
                submitBtn.classList.add('loading');

                // Optional: Change text if it's not an icon button
                const originalText = submitBtn.innerText;
                submitBtn.dataset.originalText = originalText;

                // Cleanup on page unload or if submission is canceled/failed (basic timeout fallback)
                // Note: For full AJAX forms, you'd clear this in the success/error callbacks.
                // For standard form posts, the page usually reloads so this is less critical, 
                // but we add a failsafe for history navigation (bfcache).
            }
        });
    });

    // Restore button state when navigating back (bfcache)
    window.addEventListener('pageshow', function (event) {
        if (event.persisted) {
            const loadingBtns = document.querySelectorAll('.btn.loading');
            loadingBtns.forEach(btn => {
                btn.classList.remove('loading');
                if (btn.dataset.originalText) {
                    btn.innerText = btn.dataset.originalText;
                }
            });
        }
    });

    // File input enhancement
    const fileInputs = document.querySelectorAll('.file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function () {
            // Find the display text element relative to this input
            // Assuming markup: <label class="upload-area"> <p>Text</p> <input> </label>
            const label = this.closest('.upload-area');
            if (!label) return;

            const fileNameDisplay = label.querySelector('p'); // Get the first paragraph or specific ID if unique

            if (this.files && this.files.length > 0) {
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = this.files[0].name;
                    fileNameDisplay.style.color = 'var(--text-main)';
                    fileNameDisplay.style.fontWeight = '500';
                }
            } else {
                // Handle clear selection
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = "Click to upload sheet";
                    fileNameDisplay.style.color = ''; // Reset to CSS default
                    fileNameDisplay.style.fontWeight = '';
                }
            }
        });
    });
});
