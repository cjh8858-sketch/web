// Get canvas and context
const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');
const recognizeBtn = document.getElementById('recognizeBtn');
const clearBtn = document.getElementById('clearBtn');
const resultSection = document.getElementById('resultSection');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');

// Drawing state
let isDrawing = false;
let lastX = 0;
let lastY = 0;

// Initialize canvas
function initCanvas() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
}

// Initialize on load
initCanvas();

// Mouse events for drawing
canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    lastX = e.clientX - rect.left;
    lastY = e.clientY - rect.top;
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDrawing) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();

    lastX = x;
    lastY = y;
});

canvas.addEventListener('mouseup', () => {
    isDrawing = false;
});

canvas.addEventListener('mouseout', () => {
    isDrawing = false;
});

// Touch events for mobile
canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    lastX = touch.clientX - rect.left;
    lastY = touch.clientY - rect.top;
});

canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (!isDrawing) return;

    const rect = canvas.getBoundingClientRect();
    const touch = e.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();

    lastX = x;
    lastY = y;
});

canvas.addEventListener('touchend', () => {
    isDrawing = false;
});

// Clear canvas
clearBtn.addEventListener('click', () => {
    initCanvas();
    resultSection.style.display = 'none';
    errorMessage.style.display = 'none';
});

// Recognize digit
recognizeBtn.addEventListener('click', async () => {
    // Show loading
    loading.style.display = 'flex';
    resultSection.style.display = 'none';
    errorMessage.style.display = 'none';
    recognizeBtn.disabled = true;
    clearBtn.disabled = true;

    try {
        // Get canvas image as base64
        const imageData = canvas.toDataURL('image/png');

        // Send to server
        const response = await fetch('/api/recognize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ canvas: imageData })
        });

        const data = await response.json();

        // Hide loading
        loading.style.display = 'none';

        if (data.success) {
            // Display result
            document.getElementById('resultDigit').textContent = data.digit;
            document.getElementById('resultConfidence').textContent =
                `Confidence: ${data.confidence}%`;
            resultSection.style.display = 'block';
        } else {
            // Display error
            errorMessage.textContent = `Error: ${data.error}`;
            errorMessage.style.display = 'block';
        }
    } catch (error) {
        // Hide loading
        loading.style.display = 'none';

        // Display error
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';
    } finally {
        recognizeBtn.disabled = false;
        clearBtn.disabled = false;
    }
});
