document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewArea = document.getElementById('preview-area');
    const imagePreview = document.getElementById('image-preview');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const fileDimensions = document.getElementById('file-dimensions');
    const errorMessage = document.getElementById('error-message');
    const progressContainer = document.getElementById('progress-container');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadBtn = document.getElementById('upload-btn');
    const cancelBtn = document.getElementById('cancel-btn');

    let currentFile = null;
    const MAX_SIZE = 20 * 1024 * 1024; // 20MB
    const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/heic'];

    // Format file size
    function formatBytes(bytes, decimals = 2) {
        if (!+bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }

    // Handle Drag & Drop
    dropZone.addEventListener('click', () => fileInput.click());
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('bg-white', 'border-primary'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('bg-white', 'border-primary'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        errorMessage.classList.add('d-none');
        
        // Validate type (basic)
        if (!ALLOWED_TYPES.includes(file.type) && !file.name.toLowerCase().endsWith('.heic')) {
            showError('Invalid file type. Please upload a JPG, PNG, or HEIC image.');
            return;
        }

        // Validate size
        if (file.size > MAX_SIZE) {
            showError(`File is too large (${formatBytes(file.size)}). Maximum allowed is 20MB.`);
            return;
        }

        currentFile = file;
        
        // Display info
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        
        // Generate preview and get dimensions
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            
            const img = new Image();
            img.onload = () => {
                fileDimensions.textContent = `${img.width} × ${img.height} px`;
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);

        // Switch view
        dropZone.classList.add('d-none');
        previewArea.classList.remove('d-none');
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('d-none');
    }

    cancelBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        dropZone.classList.remove('d-none');
        previewArea.classList.add('d-none');
        errorMessage.classList.add('d-none');
        progressContainer.classList.add('d-none');
        uploadProgress.style.width = '0%';
    });

    uploadBtn.addEventListener('click', () => {
        if (!currentFile) return;

        uploadBtn.disabled = true;
        cancelBtn.disabled = true;
        progressContainer.classList.remove('d-none');
        errorMessage.classList.add('d-none');

        const formData = new FormData();
        formData.append('file', currentFile);

        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                uploadProgress.style.width = percentComplete + '%';
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    window.location.href = response.redirect_url;
                } else {
                    handleUploadError(response.error || 'Upload failed');
                }
            } else {
                let errorMsg = 'Upload failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMsg = response.error || errorMsg;
                } catch (e) {}
                handleUploadError(errorMsg);
            }
        });

        xhr.addEventListener('error', () => {
            handleUploadError('Network error occurred during upload');
        });

        xhr.open('POST', window.location.pathname, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken.getAttribute('content'));
        }
        xhr.send(formData);
    });

    function handleUploadError(msg) {
        showError(msg);
        uploadBtn.disabled = false;
        cancelBtn.disabled = false;
        progressContainer.classList.add('d-none');
        uploadProgress.style.width = '0%';
    }
});
