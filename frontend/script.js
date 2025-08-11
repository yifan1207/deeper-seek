// Global variables
let map;
let earthEngineLayer = null;
let layerControl = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    setupEventListeners();
    showWelcomeMessage();
});

// Initialize Leaflet map
function initializeMap() {
    map = L.map('map', {
        center: [20, 0],
        zoom: 3,
        zoomControl: true,
        worldCopyJump: true,
        maxBounds: [[-90, -180], [90, 180]],
        maxBoundsViscosity: 1.0
    });

    // Add base tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    console.log('Map initialized successfully');
}

// Set up event listeners
function setupEventListeners() {
    // Enter key to submit
    const queryInput = document.getElementById('query-input');
    queryInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && event.ctrlKey) {
            submitQuery();
        }
    });
}

// Show welcome message
function showWelcomeMessage() {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = `
        <div class="welcome-message">
            <h3>🌍 Welcome to Earth Engine Query Interface</h3>
            <p>Enter a natural language query to analyze satellite data and visualize results on the map.</p>
            <p><strong>Try asking:</strong></p>
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li>Show me deforestation patterns in a specific region</li>
                <li>Analyze vegetation health using NDVI</li>
                <li>Display night-time lights trends over time</li>
                <li>Show Sentinel-2 imagery for a time period</li>
            </ul>
        </div>
    `;
}

// Set query from example button
function setQuery(queryText) {
    const queryInput = document.getElementById('query-input');
    queryInput.value = queryText;
    queryInput.focus();
}

// Submit query to backend
async function submitQuery() {
    const queryInput = document.getElementById('query-input');
    const queryText = queryInput.value.trim();
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const resultsContainer = document.getElementById('results-container');

    if (!queryText) {
        showError('Please enter a query');
        return;
    }

    // Show loading state
    setLoadingState(true);
    submitText.textContent = '⏳ Processing...';
    resultsContainer.innerHTML = '<div class="loading-message">🌍 Converting your query to Earth Engine code...</div>';

    try {
        const response = await fetch('/submit_query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: queryText
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
            if (data.map_data) {
                addEarthEngineLayer(data.map_data);
            }
        } else {
            showError(data.error || 'Failed to process query');
        }

    } catch (error) {
        console.error('Error submitting query:', error);
        showError('Network error. Please try again.');
    } finally {
        setLoadingState(false);
        submitText.textContent = '🚀 Run Query';
    }
}

// Display results in the UI
function displayResults(data) {
    const resultsContainer = document.getElementById('results-container');
    
    let html = `
        <div class="result-item">
            <div class="result-success">✅ ${data.response}</div>
        </div>
    `;

    // Show generated Earth Engine code
    if (data.earth_engine_code) {
        html += `
            <div class="result-item">
                <div class="code-section">
                    <span class="code-label">Generated Earth Engine Code:</span>
                    <div class="code-block">${escapeHtml(data.earth_engine_code)}</div>
                </div>
            </div>
        `;
    }

    // Show map visualization info
    if (data.map_data) {
        html += `
            <div class="result-item">
                <div class="map-info">
                    <div class="map-info-title">🗺️ Map Visualization Added</div>
                    <div><strong>Layer:</strong> ${data.map_data.layer_name || 'Earth Engine Layer'}</div>
                    ${data.map_data.mapid ? `<div><strong>Map ID:</strong> ${data.map_data.mapid.substring(0, 20)}...</div>` : ''}
                    <div style="margin-top: 8px; font-size: 13px; color: #065f46;">
                        The Earth Engine visualization has been added to the map. Use the layer control to toggle it on/off.
                    </div>
                </div>
            </div>
        `;
    }

    resultsContainer.innerHTML = html;
}

// Show error message
function showError(message) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = `
        <div class="result-item">
            <div class="result-error">❌ Error: ${escapeHtml(message)}</div>
        </div>
    `;
}

// Add Earth Engine layer to map
function addEarthEngineLayer(mapData) {
    if (!mapData.mapid || !mapData.token) {
        console.warn('Missing mapid or token for Earth Engine layer');
        return;
    }

    // Remove existing Earth Engine layer
    if (earthEngineLayer) {
        map.removeLayer(earthEngineLayer);
        if (layerControl) {
            layerControl.removeLayer(earthEngineLayer);
        }
    }

    // Create Earth Engine tile layer
    const tileUrl = `https://earthengine.googleapis.com/v1/${mapData.mapid}/tiles/{z}/{x}/{y}?token=${mapData.token}`;
    
    earthEngineLayer = L.tileLayer(tileUrl, {
        attribution: 'Google Earth Engine',
        opacity: 0.8,
        maxZoom: 18
    });

    // Add layer to map
    earthEngineLayer.addTo(map);

    // Create or update layer control
    const layerName = mapData.layer_name || 'Earth Engine Layer';
    
    if (!layerControl) {
        layerControl = L.control.layers(null, {}).addTo(map);
    }
    
    layerControl.addOverlay(earthEngineLayer, layerName);

    // Center map based on layer type
    centerMapForLayer(mapData);

    console.log(`Earth Engine layer "${layerName}" added to map`);
}

// Center map based on layer type
function centerMapForLayer(mapData) {
    const layerName = (mapData.layer_name || '').toLowerCase();
    
    if (layerName.includes('amazon')) {
        map.setView([-3.4, -60.0], 6);
    } else if (layerName.includes('lights') || layerName.includes('night')) {
        map.setView([20, 0], 3);
    } else if (layerName.includes('brazil')) {
        map.setView([-14.2, -51.9], 5);
    } else if (layerName.includes('sentinel') || layerName.includes('landsat')) {
        map.setView([20, 0], 3);
    } else {
        // Default global view
        map.setView([20, 0], 3);
    }
}

// Clear all Earth Engine layers
function clearEarthEngineLayers() {
    if (earthEngineLayer) {
        map.removeLayer(earthEngineLayer);
        if (layerControl) {
            layerControl.removeLayer(earthEngineLayer);
        }
        earthEngineLayer = null;
        console.log('Earth Engine layer cleared');
    }
    
    // Reset results
    showWelcomeMessage();
}

// Set loading state
function setLoadingState(loading) {
    const submitBtn = document.getElementById('submit-btn');
    const container = document.querySelector('.container');
    
    submitBtn.disabled = loading;
    
    if (loading) {
        container.classList.add('loading');
    } else {
        container.classList.remove('loading');
    }
}

// Utility function to escape HTML
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}