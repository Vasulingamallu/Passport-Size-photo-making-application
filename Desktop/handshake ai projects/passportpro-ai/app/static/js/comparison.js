function initComparisonSlider(containerId, beforeSrc, afterSrc) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="comparison-wrapper" style="position: relative; width: 100%; height: 100%; overflow: hidden; border-radius: 8px;">
            <img src="${afterSrc}" alt="After" style="width: 100%; height: 100%; object-fit: contain; display: block;">
            <div class="comparison-before" style="position: absolute; top: 0; left: 0; width: 50%; height: 100%; overflow: hidden;">
                <img src="${beforeSrc}" alt="Before" style="width: ${container.offsetWidth}px; height: 100%; object-fit: contain; display: block; max-width: none;">
            </div>
            <div class="comparison-slider" style="position: absolute; top: 0; left: 50%; width: 4px; height: 100%; background: white; cursor: ew-resize; z-index: 10; transform: translateX(-50%); box-shadow: 0 0 5px rgba(0,0,0,0.5);">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 30px; height: 30px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 5px rgba(0,0,0,0.5);">
                    <i class="bi bi-chevron-left text-dark" style="font-size: 10px;"></i>
                    <i class="bi bi-chevron-right text-dark" style="font-size: 10px;"></i>
                </div>
            </div>
        </div>
    `;

    const wrapper = container.querySelector('.comparison-wrapper');
    const beforeDiv = container.querySelector('.comparison-before');
    const beforeImg = beforeDiv.querySelector('img');
    const slider = container.querySelector('.comparison-slider');

    let isDown = false;

    // Handle Resize
    window.addEventListener('resize', () => {
        beforeImg.style.width = wrapper.offsetWidth + 'px';
    });

    slider.addEventListener('mousedown', (e) => {
        isDown = true;
    });

    window.addEventListener('mouseup', () => {
        isDown = false;
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        const rect = wrapper.getBoundingClientRect();
        let x = e.pageX - rect.left;
        
        // Boundaries
        x = Math.max(0, Math.min(x, rect.width));
        
        const percent = (x / rect.width) * 100;
        beforeDiv.style.width = `${percent}%`;
        slider.style.left = `${percent}%`;
    });

    // Touch support
    slider.addEventListener('touchstart', (e) => {
        isDown = true;
    });

    window.addEventListener('touchend', () => {
        isDown = false;
    });

    window.addEventListener('touchmove', (e) => {
        if (!isDown) return;
        const rect = wrapper.getBoundingClientRect();
        let x = e.touches[0].pageX - rect.left;
        
        x = Math.max(0, Math.min(x, rect.width));
        
        const percent = (x / rect.width) * 100;
        beforeDiv.style.width = `${percent}%`;
        slider.style.left = `${percent}%`;
    });
}
