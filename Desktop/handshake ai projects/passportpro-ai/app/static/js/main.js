document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(msg);
            bsAlert.close();
        }, 5000);
    });
});

const utils = {
    showSpinner: function(elementId) {
        const el = document.getElementById(elementId);
        if(el) {
            el.innerHTML = '<div class="spinner-border spinner-border-sm text-light" role="status"><span class="visually-hidden">Loading...</span></div>';
            el.disabled = true;
        }
    },
    
    hideSpinner: function(elementId, originalText) {
        const el = document.getElementById(elementId);
        if(el) {
            el.innerHTML = originalText;
            el.disabled = false;
        }
    },

    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    showToast: function(message, type = 'info') {
        console.log(`[${type}] ${message}`);
    },

    previewImage: function(input, previewElementId) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById(previewElementId);
                if(preview) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
            }
            reader.readAsDataURL(input.files[0]);
        }
    },
    
    confirmAction: function(message) {
        return confirm(message);
    }
};
