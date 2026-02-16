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

                // Add loading class and spinner
                submitBtn.classList.add('loading');

                // Save original content
                const originalContent = submitBtn.innerHTML;
                submitBtn.dataset.originalContent = originalContent;

                // Determine loading text based on current text
                const btnText = submitBtn.innerText.trim().toLowerCase();
                let loadingText = "Processing...";

                if (btnText.includes("sign in") || btnText.includes("login")) {
                    loadingText = "Signing In...";
                } else if (btnText.includes("create account") || btnText.includes("register")) {
                    loadingText = "Creating Account...";
                } else if (btnText.includes("save")) {
                    loadingText = "Saving...";
                } else if (btnText.includes("update")) {
                    loadingText = "Updating...";
                } else if (btnText.includes("upload")) {
                    loadingText = "Uploading...";
                }

                // Inject text only
                submitBtn.innerText = loadingText;
            }
        });
    });

    // Restore button state when navigating back (bfcache)
    window.addEventListener('pageshow', function (event) {
        // Always check for loading buttons regardless of persistence
        const loadingBtns = document.querySelectorAll('.btn.loading');
        loadingBtns.forEach(btn => {
            btn.classList.remove('loading');
            if (btn.dataset.originalContent) {
                btn.innerHTML = btn.dataset.originalContent;
            }
        });
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
