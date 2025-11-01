// LED Neon Control - Frontend JavaScript

// State
let currentEffect = 'off';
let currentBrightness = 50;
let currentColor = { r: 255, g: 0, b: 0 };

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeUI();
    loadStatus();
    startSensorUpdates();
    startClockUpdates();
});

// Initialize UI event listeners
function initializeUI() {
    // Effect buttons
    const effectButtons = document.querySelectorAll('.effect-btn');
    effectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const effect = this.getAttribute('data-effect');
            setEffect(effect);
        });
    });

    // Color slider
    const colorSlider = document.getElementById('color-slider');
    const colorPreview = document.getElementById('color-preview');
    
    colorSlider.addEventListener('input', function() {
        updateColorPreview(this.value);
    });
    
    // Apply color button
    document.getElementById('apply-color').addEventListener('click', function() {
        applyColor();
    });

    // Brightness slider
    const brightnessSlider = document.getElementById('brightness-slider');
    const brightnessValue = document.getElementById('brightness-value');
    
    brightnessSlider.addEventListener('input', function() {
        brightnessValue.textContent = this.value;
        setBrightness(this.value);
    });

    // Initialize color preview
    updateColorPreview(0);
}

// API Functions
async function setEffect(effect) {
    try {
        const response = await fetch('/api/effect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ effect: effect })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentEffect = effect;
            updateEffectButtons();
            updateStatus();
        } else {
            console.error('Error setting effect:', data.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function setBrightness(value) {
    try {
        const response = await fetch('/api/brightness', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ brightness: parseInt(value) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentBrightness = data.brightness;
            document.getElementById('current-brightness').textContent = currentBrightness + '%';
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function applyColor() {
    try {
        const response = await fetch('/api/color', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentColor)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // If not in static mode, switch to it
            if (currentEffect !== 'static') {
                await setEffect('static');
            } else {
                // Just trigger the effect again to update color
                await setEffect('static');
            }
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        currentEffect = data.effect;
        currentBrightness = data.brightness;
        currentColor = { r: data.color[0], g: data.color[1], b: data.color[2] };
        
        updateStatus();
        updateEffectButtons();
        
        // Update brightness slider
        document.getElementById('brightness-slider').value = currentBrightness;
        document.getElementById('brightness-value').textContent = currentBrightness;
        
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

async function getSensorData() {
    try {
        const response = await fetch('/api/sensor');
        const data = await response.json();
        
        document.getElementById('temperature').textContent = data.temperature.toFixed(1);
        document.getElementById('pressure').textContent = data.pressure.toFixed(1);
    } catch (error) {
        console.error('Error loading sensor data:', error);
    }
}

// UI Update Functions
function updateStatus() {
    document.getElementById('current-effect').textContent = currentEffect;
    document.getElementById('current-brightness').textContent = currentBrightness + '%';
}

function updateEffectButtons() {
    const effectButtons = document.querySelectorAll('.effect-btn');
    effectButtons.forEach(button => {
        const effect = button.getAttribute('data-effect');
        if (effect === currentEffect) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

function updateColorPreview(hue) {
    const color = hsvToRgb(hue / 360, 1.0, 1.0);
    currentColor = color;
    
    const colorPreview = document.getElementById('color-preview');
    const rgbString = `rgb(${color.r}, ${color.g}, ${color.b})`;
    colorPreview.style.backgroundColor = rgbString;
    colorPreview.style.boxShadow = `0 0 20px ${rgbString}`;
}

// Color conversion
function hsvToRgb(h, s, v) {
    let r, g, b;
    
    const i = Math.floor(h * 6);
    const f = h * 6 - i;
    const p = v * (1 - s);
    const q = v * (1 - f * s);
    const t = v * (1 - (1 - f) * s);
    
    switch (i % 6) {
        case 0: r = v; g = t; b = p; break;
        case 1: r = q; g = v; b = p; break;
        case 2: r = p; g = v; b = t; break;
        case 3: r = p; g = q; b = v; break;
        case 4: r = t; g = p; b = v; break;
        case 5: r = v; g = p; b = q; break;
    }
    
    return {
        r: Math.round(r * 255),
        g: Math.round(g * 255),
        b: Math.round(b * 255)
    };
}

// Clock update
function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    document.getElementById('clock-time').textContent = `${hours}:${minutes}:${seconds}`;
}

// Periodic updates
function startSensorUpdates() {
    getSensorData();
    setInterval(getSensorData, 2000); // Update every 2 seconds
}

function startClockUpdates() {
    updateClock();
    setInterval(updateClock, 1000); // Update every second
}
