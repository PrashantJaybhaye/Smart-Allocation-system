document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');

        // Function to check validity and toggle button
        const checkFormValidity = () => {
            if (!submitBtn) return;

            // Only apply Strict validation disabling for "Create Account"
            const btnText = submitBtn.innerText.trim().toLowerCase();
            if (!btnText.includes("create account") && !btnText.includes("register")) {
                return;
            }

            if (form.checkValidity()) {
                submitBtn.removeAttribute('disabled');
                submitBtn.classList.remove('btn-disabled'); // Optional styling class
                submitBtn.style.opacity = '1';
                submitBtn.style.cursor = 'pointer';
            } else {
                submitBtn.setAttribute('disabled', 'true');
                submitBtn.classList.add('btn-disabled');
                submitBtn.style.opacity = '0.5';
                submitBtn.style.cursor = 'not-allowed';
            }
        };

        // Initial check
        checkFormValidity();

        // Listen for input changes
        form.addEventListener('input', checkFormValidity);
        form.addEventListener('change', checkFormValidity);

        form.addEventListener('submit', function (event) {
            // content of the submit listener remains the same...
            // Check if form is valid (if using browser validation)
            if (!form.checkValidity()) {
                // If form is invalid, browser shows error, don't show loading
                event.preventDefault(); // Ensure it doesn't submit
                return;
            }

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
