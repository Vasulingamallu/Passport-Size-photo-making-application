document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('photo-canvas');
    const preview = document.getElementById('photo-preview');
    const captureBtn = document.getElementById('capture-btn');
    const switchCameraBtn = document.getElementById('switch-camera-btn');
    const retakeBtn = document.getElementById('retake-btn');
    const usePhotoBtn = document.getElementById('use-photo-btn');
    const cameraContainer = document.getElementById('camera-container');
    const previewContainer = document.getElementById('preview-container');
    const cameraControls = document.getElementById('camera-controls');
    const previewControls = document.getElementById('preview-controls');
    const errorMessage = document.getElementById('error-message');

    let stream = null;
    let currentFacingMode = 'user';
    let imageData = null;

    async function initCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: currentFacingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            video.srcObject = stream;
            errorMessage.classList.add('d-none');
        } catch (err) {
            console.error('Error accessing camera:', err);
            errorMessage.textContent = 'Unable to access camera. Please check permissions or try uploading a file instead.';
            errorMessage.classList.remove('d-none');
            captureBtn.disabled = true;
            switchCameraBtn.disabled = true;
        }
    }

    switchCameraBtn.addEventListener('click', () => {
        currentFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';
        initCamera();
    });

    captureBtn.addEventListener('click', () => {
        if (!stream) return;
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        
        if (currentFacingMode === 'user') {
            // Mirror image for front camera
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
        }
        
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        imageData = canvas.toDataURL('image/jpeg', 0.9);
        preview.src = imageData;
        
        cameraContainer.classList.add('d-none');
        cameraControls.classList.add('d-none');
        previewContainer.classList.remove('d-none');
        previewControls.classList.remove('d-none');
        
        // Pause stream processing to save resources
        stream.getTracks().forEach(track => track.enabled = false);
    });

    retakeBtn.addEventListener('click', () => {
        imageData = null;
        cameraContainer.classList.remove('d-none');
        cameraControls.classList.remove('d-none');
        previewContainer.classList.add('d-none');
        previewControls.classList.add('d-none');
        
        if (stream) {
            stream.getTracks().forEach(track => track.enabled = true);
        } else {
            initCamera();
        }
    });

    usePhotoBtn.addEventListener('click', async () => {
        if (!imageData) return;
        
        usePhotoBtn.disabled = true;
        usePhotoBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Uploading...';
        retakeBtn.disabled = true;
        
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]') ? document.querySelector('meta[name="csrf-token"]').getAttribute('content') : '';
            const response = await fetch(captureUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ image: imageData })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                window.location.href = result.redirect_url;
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (err) {
            console.error('Upload error:', err);
            errorMessage.textContent = err.message;
            errorMessage.classList.remove('d-none');
            usePhotoBtn.disabled = false;
            usePhotoBtn.textContent = 'Use Photo';
            retakeBtn.disabled = false;
        }
    });

    // Cleanup on page leave
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });

    // Start camera
    initCamera();
});
