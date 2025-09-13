/**
 * AI Land Use Classification MVP
 * Phase 4: Web Map Frontend
 * 
 * Interactive Leaflet.js map with land use classification data
 */

class LandUseMap {
    constructor() {
        this.map = null;
        this.landUseLayer = null;
        this.layers = {
            water: null,
            forest: null,
            agriculture: null
        };
        this.classStyles = {
            water: {
                color: '#0066cc',
                fillColor: '#0066cc',
                fillOpacity: 0.7,
                weight: 2
            },
            forest: {
                color: '#00aa00',
                fillColor: '#00aa00',
                fillOpacity: 0.7,
                weight: 2
            },
            agriculture: {
                color: '#ffaa00',
                fillColor: '#ffaa00',
                fillOpacity: 0.7,
                weight: 2
            }
        };
        
        this.init();
    }
    
    init() {
        this.initializeMap();
        this.setupEventListeners();
        this.loadData();
    }
    
    initializeMap() {
        // Initialize map centered on Telangana, India
        this.map = L.map('map').setView([18.1124, 79.0193], 8);
        
        // Add OpenStreetMap base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        // Add legend
        this.addLegend();
    }
    
    addLegend() {
        const legend = L.control({position: 'bottomright'});
        
        legend.onAdd = (map) => {
            const div = L.DomUtil.create('div', 'legend');
            div.innerHTML = `
                <h4>Land Use Classes</h4>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.water.fillColor}"></div>
                    <span>Water</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.forest.fillColor}"></div>
                    <span>Forest</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.agriculture.fillColor}"></div>
                    <span>Agriculture</span>
                </div>
            `;
            return div;
        };
        
        legend.addTo(this.map);
    }
    
    setupEventListeners() {
        // Main layer toggle
        const layerToggle = document.getElementById('layer-toggle');
        layerToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.showAllLayers();
            } else {
                this.hideAllLayers();
            }
        });
        
        // Individual class toggles
        const classToggles = {
            'water-toggle': 'water',
            'forest-toggle': 'forest',
            'agriculture-toggle': 'agriculture'
        };
        
        Object.entries(classToggles).forEach(([toggleId, className]) => {
            const toggle = document.getElementById(toggleId);
            toggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.showLayer(className);
                } else {
                    this.hideLayer(className);
                }
            });
        });
    }
    
    async loadData() {
        const statusElement = document.getElementById('status');
        statusElement.textContent = 'Loading data...';
        statusElement.className = 'status loading';
        
        try {
            // Check if data is available
            const statusResponse = await fetch('/status');
            const status = await statusResponse.json();
            
            if (!status.data_available) {
                throw new Error('No classified data available. Please run the classification script first.');
            }
            
            // Load the GeoJSON data
            const response = await fetch('/data');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.processData(data);
            statusElement.textContent = `Loaded ${data.features.length} land use features`;
            statusElement.className = 'status success';
            
        } catch (error) {
            console.error('Error loading data:', error);
            statusElement.textContent = `Error: ${error.message}`;
            statusElement.className = 'status error';
        }
    }
    
    processData(geojsonData) {
        // Group features by class
        const featuresByClass = {
            water: [],
            forest: [],
            agriculture: []
        };
        
        geojsonData.features.forEach(feature => {
            const className = feature.properties.class;
            if (featuresByClass[className]) {
                featuresByClass[className].push(feature);
            }
        });
        
        // Create separate layers for each class
        Object.entries(featuresByClass).forEach(([className, features]) => {
            if (features.length > 0) {
                this.layers[className] = L.geoJSON(features, {
                    style: this.classStyles[className],
                    onEachFeature: (feature, layer) => {
                        // Add popup with class information
                        layer.bindPopup(`
                            <strong>Land Use Class:</strong> ${feature.properties.class}<br>
                            <strong>Class ID:</strong> ${feature.properties.class_id}
                        `);
                    }
                });
            }
        });
        
        // Add all layers to map
        this.showAllLayers();
    }
    
    showAllLayers() {
        Object.values(this.layers).forEach(layer => {
            if (layer) {
                this.map.addLayer(layer);
            }
        });
    }
    
    hideAllLayers() {
        Object.values(this.layers).forEach(layer => {
            if (layer) {
                this.map.removeLayer(layer);
            }
        });
    }
    
    showLayer(className) {
        const layer = this.layers[className];
        if (layer && !this.map.hasLayer(layer)) {
            this.map.addLayer(layer);
        }
    }
    
    hideLayer(className) {
        const layer = this.layers[className];
        if (layer && this.map.hasLayer(layer)) {
            this.map.removeLayer(layer);
        }
    }
}

// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new LandUseMap();
});
