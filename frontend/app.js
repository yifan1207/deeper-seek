// Main application for Satellite Embeddings Similarity Search
class SatelliteSimilarityApp {
    constructor() {
        this.map = null;
        this.ee = null;
        this.currentYear = 2024;
        this.currentPalette = 'viridis';
        this.selectedPoint = null;
        this.isLoading = false;
        this.eeInitialized = false;
        
        this.palettes = {
            viridis: ['000004', '2C105C', '711F81', 'B63679', 'EE605E', 'FDAE78', 'FCFDBF', 'FFFFFF'],
            plasma: ['0D0887', '46039F', '7201A8', '9C179E', 'BD3786', 'D8576B', 'ED7953', 'FDB42F', 'F0F921'],
            inferno: ['000004', '1B0C41', '4A0C6B', '781C6D', 'A52C60', 'CF4446', 'ED6925', 'FB9B06', 'F7E225']
        };
        
        this.init();
    }

    async init() {
        try {
            // First initialize the map (this doesn't require Earth Engine)
            this.initializeMap();
            this.setupEventListeners();
            
            // Then try to initialize Earth Engine
            await this.initializeEarthEngine();
            
            this.hideLoadingSpinner();
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.showError('Failed to load Earth Engine. Please check your connection and try again.');
            this.hideLoadingSpinner();
        }
    }

    initializeMap() {
        // Initialize map without Earth Engine dependency
        this.map = new google.maps.Map(document.getElementById('map'), {
            center: { lat: 0, lng: 0 },
            zoom: 2,
            mapTypeId: google.maps.MapTypeId.SATELLITE,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false
        });
    }

    async initializeEarthEngine() {
        // Check if Earth Engine API is loaded
        if (typeof ee === 'undefined') {
            throw new Error('Earth Engine API not loaded');
        }

        try {
            // Initialize Earth Engine
            await new Promise((resolve, reject) => {
                ee.initialize(() => {
                    console.log('Earth Engine initialized successfully');
                    this.eeInitialized = true;
                    resolve();
                }, (error) => {
                    console.error('Earth Engine initialization failed:', error);
                    reject(error);
                });
            });

            // Add Earth Engine layer
            this.updateMapLayer();
        } catch (error) {
            console.error('Earth Engine initialization error:', error);
            // Don't throw - allow the app to work without Earth Engine
            this.eeInitialized = false;
        }
    }

    setupEventListeners() {
        // Map click handler
        this.map.addListener('click', (event) => {
            this.handleMapClick(event.latLng);
        });

        // Control panel event listeners
        document.getElementById('yearSelect').addEventListener('change', (e) => {
            this.currentYear = parseInt(e.target.value);
            if (this.eeInitialized) {
                this.updateMapLayer();
            }
        });

        document.getElementById('paletteSelect').addEventListener('change', (e) => {
            this.currentPalette = e.target.value;
            this.updateLegend();
            if (this.selectedPoint && this.eeInitialized) {
                this.updateSimilarityLayer();
            }
        });

        // Zoom change handler
        this.map.addListener('zoom_changed', () => {
            const zoom = this.map.getZoom();
            this.updateURLParams({ zoom });
        });
    }

    async handleMapClick(latLng) {
        if (this.isLoading) return;

        this.selectedPoint = {
            lat: latLng.lat(),
            lng: latLng.lng()
        };

        this.updateCoordinates();
        this.showLoadingSpinner();
        this.isLoading = true;

        try {
            if (this.eeInitialized) {
                await this.calculateSimilarity();
            } else {
                // Simulate processing if Earth Engine is not available
                await new Promise(resolve => setTimeout(resolve, 2000));
                this.showError('Earth Engine not available. This is a demo mode.');
            }
            
            this.updateURLParams({
                lat: this.selectedPoint.lat,
                lng: this.selectedPoint.lng,
                clicked: 'true'
            });
        } catch (error) {
            console.error('Error calculating similarity:', error);
            this.showError('Failed to calculate similarity. Please try again.');
        } finally {
            this.hideLoadingSpinner();
            this.isLoading = false;
        }
    }

    async calculateSimilarity() {
        if (!this.eeInitialized) {
            throw new Error('Earth Engine not initialized');
        }

        // This would integrate with Earth Engine API
        // For now, we'll simulate the process
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Update similarity layer (simulated)
        this.updateSimilarityLayer();
        
        // Update thumbnail (simulated)
        this.updateThumbnail();
    }

    updateMapLayer() {
        if (!this.eeInitialized) {
            console.log('Earth Engine not available - skipping map layer update');
            return;
        }
        
        // This would update the Earth Engine layer based on current year
        console.log(`Updating map layer for year: ${this.currentYear}`);
    }

    updateSimilarityLayer() {
        // This would update the similarity visualization
        console.log(`Updating similarity layer with palette: ${this.currentPalette}`);
    }

    updateLegend() {
        const gradient = document.getElementById('legendGradient');
        const palette = this.palettes[this.currentPalette];
        
        if (gradient && palette) {
            const gradientString = palette.map(color => `#${color}`).join(', ');
            gradient.style.background = `linear-gradient(to right, ${gradientString})`;
        }
    }

    updateCoordinates() {
        const coordsElement = document.getElementById('coordinates');
        if (coordsElement && this.selectedPoint) {
            coordsElement.textContent = `${this.selectedPoint.lat.toFixed(4)}, ${this.selectedPoint.lng.toFixed(4)}`;
        }
    }

    updateThumbnail() {
        const container = document.getElementById('thumbnailContainer');
        if (container && this.selectedPoint) {
            // Simulate thumbnail generation
            container.innerHTML = `
                <div style="text-align: center; padding: 1rem;">
                    <div style="width: 200px; height: 120px; background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 8px; margin-bottom: 0.5rem;"></div>
                    <p style="font-size: 0.8rem; color: #6c757d;">Sentinel-2 Composite</p>
                </div>
            `;
        }
    }

    updateURLParams(params) {
        const url = new URL(window.location);
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.set(key, value);
        });
        window.history.replaceState({}, '', url);
    }

    showLoadingSpinner() {
        const overlay = document.querySelector('.map-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }

    hideLoadingSpinner() {
        const overlay = document.querySelector('.map-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }

    showError(message) {
        // Create and show error notification
        const notification = document.createElement('div');
        notification.className = 'error-notification fade-in';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 3000;
            max-width: 300px;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    restoreFromURL() {
        const url = new URL(window.location);
        const lat = url.searchParams.get('lat');
        const lng = url.searchParams.get('lng');
        const clicked = url.searchParams.get('clicked');
        const zoom = url.searchParams.get('zoom');

        if (lat && lng && clicked === 'true') {
            const latLng = { lat: parseFloat(lat), lng: parseFloat(lng) };
            this.map.setCenter(latLng);
            if (zoom) {
                this.map.setZoom(parseInt(zoom));
            }
            this.handleMapClick(latLng);
        }
    }
}

// Modal functions
function showAbout() {
    document.getElementById('aboutModal').style.display = 'block';
}

function showHelp() {
    document.getElementById('helpModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new SatelliteSimilarityApp();
    
    // Restore state from URL
    setTimeout(() => {
        app.restoreFromURL();
    }, 1000);
    
    // Make app globally available for debugging
    window.app = app;
});

// Error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});
