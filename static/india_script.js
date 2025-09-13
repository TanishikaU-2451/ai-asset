/**
 * Enhanced AI Land Use Classification for India
 * Interactive web application with advanced features
 */

class IndiaLandUseMap {
    constructor() {
        this.map = null;
        this.layers = {};
        this.currentFilters = {};
        this.statistics = {};
        this.fraProgress = {};
        
        // Enhanced class styles for India
        this.classStyles = {
            'water': { color: '#0066cc', fillColor: '#0066cc', fillOpacity: 0.7, weight: 2 },
            'forest_dense': { color: '#00aa00', fillColor: '#00aa00', fillOpacity: 0.7, weight: 2 },
            'forest_open': { color: '#66cc00', fillColor: '#66cc00', fillOpacity: 0.7, weight: 2 },
            'agriculture_irrigated': { color: '#ffaa00', fillColor: '#ffaa00', fillOpacity: 0.7, weight: 2 },
            'agriculture_rainfed': { color: '#ffcc66', fillColor: '#ffcc66', fillOpacity: 0.7, weight: 2 },
            'urban': { color: '#cc0000', fillColor: '#cc0000', fillOpacity: 0.7, weight: 2 },
            'grassland': { color: '#99cc00', fillColor: '#99cc00', fillOpacity: 0.7, weight: 2 },
            'wasteland': { color: '#cc9900', fillColor: '#cc9900', fillOpacity: 0.7, weight: 2 },
            'wetland': { color: '#006699', fillColor: '#006699', fillOpacity: 0.7, weight: 2 },
            'mangrove': { color: '#009966', fillColor: '#009966', fillOpacity: 0.7, weight: 2 },
            'fra_area': { color: '#9900cc', fillColor: '#9900cc', fillOpacity: 0.8, weight: 3 }
        };
        
        this.init();
    }
    
    async init() {
        this.initializeMap();
        this.setupEventListeners();
        await this.loadInitialData();
    }
    
    initializeMap() {
        // Initialize map centered on India
        this.map = L.map('map').setView([20.5937, 78.9629], 5);
        
        // Add OpenStreetMap base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        // Add scale control
        L.control.scale().addTo(this.map);
        
        // Add legend
        this.addLegend();
        
        // Update scale display
        this.map.on('zoomend', () => {
            this.updateScaleDisplay();
        });
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
                    <div class="legend-color" style="background-color: ${this.classStyles.forest_dense.fillColor}"></div>
                    <span>Dense Forest</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.forest_open.fillColor}"></div>
                    <span>Open Forest</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.agriculture_irrigated.fillColor}"></div>
                    <span>Irrigated Agriculture</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.agriculture_rainfed.fillColor}"></div>
                    <span>Rainfed Agriculture</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.urban.fillColor}"></div>
                    <span>Urban</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.classStyles.fra_area.fillColor}"></div>
                    <span>FRA Areas</span>
                </div>
            `;
            return div;
        };
        
        legend.addTo(this.map);
    }
    
    setupEventListeners() {
        // Filter controls
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });
        
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Export data
        document.getElementById('export-data').addEventListener('click', () => {
            this.exportData();
        });
        
        // Fullscreen
        document.getElementById('fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });
        
        // Modal controls
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.style.display = 'none';
            }
        });
    }
    
    async loadInitialData() {
        try {
            // Load filter options
            await this.loadFilterOptions();
            
            // Load layer information
            await this.loadLayers();
            
            // Load initial data
            await this.loadData();
            
            // Load statistics
            await this.loadStatistics();
            
            // Load FRA progress
            await this.loadFRAProgress();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load initial data');
        }
    }
    
    async loadFilterOptions() {
        try {
            const response = await fetch('/api/filter-options');
            const options = await response.json();
            
            // Populate filter dropdowns
            this.populateSelect('state-filter', options.states);
            this.populateSelect('district-filter', options.districts);
            this.populateSelect('village-filter', options.villages);
            this.populateSelect('tribal-filter', options.tribal_communities);
            this.populateSelect('class-filter', options.classes);
            this.populateSelect('fra-type-filter', options.fra_types);
            this.populateSelect('status-filter', options.claim_statuses);
            
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    }
    
    populateSelect(selectId, options) {
        const select = document.getElementById(selectId);
        if (!select || !options) return;
        
        // Clear existing options except first
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Add new options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }
    
    async loadLayers() {
        try {
            const response = await fetch('/api/layers');
            const layers = await response.json();
            
            const layerControls = document.getElementById('layer-controls');
            layerControls.innerHTML = '';
            
            Object.entries(layers).forEach(([key, layer]) => {
                const layerItem = document.createElement('div');
                layerItem.className = 'layer-item';
                layerItem.innerHTML = `
                    <input type="checkbox" class="layer-checkbox" id="layer-${key}" ${layer.visible ? 'checked' : ''}>
                    <span class="layer-name">${layer.name}</span>
                    <span class="layer-count" id="count-${key}">0</span>
                `;
                
                layerItem.addEventListener('change', (e) => {
                    this.toggleLayer(key, e.target.checked);
                });
                
                layerControls.appendChild(layerItem);
            });
            
        } catch (error) {
            console.error('Error loading layers:', error);
        }
    }
    
    async loadData() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`/api/data?${params}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.processData(data);
            this.updateFeatureCount(data.features.length);
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load data');
        }
    }
    
    processData(geojsonData) {
        // Clear existing layers
        Object.values(this.layers).forEach(layer => {
            if (layer && this.map.hasLayer(layer)) {
                this.map.removeLayer(layer);
            }
        });
        this.layers = {};
        
        // Group features by class
        const featuresByClass = {};
        
        geojsonData.features.forEach(feature => {
            const className = feature.properties.class;
            if (!featuresByClass[className]) {
                featuresByClass[className] = [];
            }
            featuresByClass[className].push(feature);
        });
        
        // Create layers for each class
        Object.entries(featuresByClass).forEach(([className, features]) => {
            if (features.length > 0) {
                this.layers[className] = L.geoJSON(features, {
                    style: this.classStyles[className] || this.classStyles.fra_area,
                    onEachFeature: (feature, layer) => {
                        this.addPopup(feature, layer);
                    }
                });
                
                // Add to map if layer is enabled
                const layerCheckbox = document.getElementById(`layer-${className}`);
                if (layerCheckbox && layerCheckbox.checked) {
                    this.map.addLayer(this.layers[className]);
                }
                
                // Update layer count
                const countElement = document.getElementById(`count-${className}`);
                if (countElement) {
                    countElement.textContent = features.length;
                }
            }
        });
    }
    
    addPopup(feature, layer) {
        const props = feature.properties;
        let popupContent = `<div class="popup-title">${props.class || 'Unknown'}</div>`;
        
        // Add class-specific information
        if (props.state) popupContent += `<div class="popup-details"><span class="popup-label">State:</span> <span class="popup-value">${props.state}</span></div>`;
        if (props.district) popupContent += `<div class="popup-details"><span class="popup-label">District:</span> <span class="popup-value">${props.district}</span></div>`;
        if (props.village) popupContent += `<div class="popup-details"><span class="popup-label">Village:</span> <span class="popup-value">${props.village}</span></div>`;
        if (props.area_km2) popupContent += `<div class="popup-details"><span class="popup-label">Area:</span> <span class="popup-value">${props.area_km2} km²</span></div>`;
        if (props.confidence) popupContent += `<div class="popup-details"><span class="popup-label">Confidence:</span> <span class="popup-value">${(props.confidence * 100).toFixed(1)}%</span></div>`;
        
        // FRA specific information
        if (props.fra_type) {
            popupContent += `<div class="popup-details"><span class="popup-label">FRA Type:</span> <span class="popup-value">${props.fra_type}</span></div>`;
        }
        if (props.claim_status) {
            const statusClass = props.claim_status.toLowerCase();
            popupContent += `<div class="popup-details">
                <span class="popup-label">Status:</span> 
                <span class="popup-value">
                    <span class="status-indicator ${statusClass}"></span>${props.claim_status}
                </span>
            </div>`;
        }
        if (props.tribal_community) {
            popupContent += `<div class="popup-details"><span class="popup-label">Tribal Community:</span> <span class="popup-value">${props.tribal_community}</span></div>`;
        }
        
        layer.bindPopup(popupContent);
    }
    
    toggleLayer(layerName, visible) {
        const layer = this.layers[layerName];
        if (layer) {
            if (visible) {
                this.map.addLayer(layer);
            } else {
                this.map.removeLayer(layer);
            }
        }
    }
    
    applyFilters() {
        // Collect filter values
        this.currentFilters = {
            state: document.getElementById('state-filter').value,
            district: document.getElementById('district-filter').value,
            village: document.getElementById('village-filter').value,
            tribal_group: document.getElementById('tribal-filter').value,
            class: document.getElementById('class-filter').value,
            fra_type: document.getElementById('fra-type-filter').value,
            claim_status: document.getElementById('status-filter').value
        };
        
        // Remove empty filters
        this.currentFilters = Object.fromEntries(
            Object.entries(this.currentFilters).filter(([_, value]) => value)
        );
        
        // Reload data with filters
        this.loadData();
    }
    
    clearFilters() {
        // Reset all filter dropdowns
        document.getElementById('state-filter').value = '';
        document.getElementById('district-filter').value = '';
        document.getElementById('village-filter').value = '';
        document.getElementById('tribal-filter').value = '';
        document.getElementById('class-filter').value = '';
        document.getElementById('fra-type-filter').value = '';
        document.getElementById('status-filter').value = '';
        
        // Clear current filters
        this.currentFilters = {};
        
        // Reload data
        this.loadData();
    }
    
    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics');
            const stats = await response.json();
            
            this.statistics = stats;
            this.updateStatisticsPanel(stats);
            
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }
    
    updateStatisticsPanel(stats) {
        const statsPanel = document.getElementById('stats-panel');
        if (!statsPanel) return;
        
        let html = '';
        
        if (stats.total_features) {
            html += `<div class="stat-item">
                <span class="stat-label">Total Features:</span>
                <span class="stat-value">${stats.total_features.toLocaleString()}</span>
            </div>`;
        }
        
        if (stats.class_distribution) {
            html += '<div class="stat-item"><span class="stat-label">Land Use Classes:</span></div>';
            Object.entries(stats.class_distribution).forEach(([className, count]) => {
                html += `<div class="stat-item" style="margin-left: 15px;">
                    <span class="stat-label">${className}:</span>
                    <span class="stat-value">${count}</span>
                </div>`;
            });
        }
        
        if (stats.fra_statistics && stats.fra_statistics.total_claims) {
            html += `<div class="stat-item">
                <span class="stat-label">FRA Claims:</span>
                <span class="stat-value">${stats.fra_statistics.total_claims}</span>
            </div>`;
        }
        
        statsPanel.innerHTML = html || '<div class="loading">No statistics available</div>';
    }
    
    async loadFRAProgress() {
        try {
            const response = await fetch('/api/fra-progress');
            const progress = await response.json();
            
            this.fraProgress = progress;
            this.updateFRAProgressPanel(progress);
            
        } catch (error) {
            console.error('Error loading FRA progress:', error);
        }
    }
    
    updateFRAProgressPanel(progress) {
        const fraPanel = document.getElementById('fra-progress');
        if (!fraPanel) return;
        
        let html = '';
        
        if (progress.overall) {
            html += '<div class="fra-level"><h5>Overall Progress</h5>';
            html += '<div class="fra-stats">';
            Object.entries(progress.overall).forEach(([status, count]) => {
                html += `<div class="fra-stat ${status}">${status}: ${count}</div>`;
            });
            html += '</div></div>';
        }
        
        if (progress.state_level) {
            html += '<div class="fra-level"><h5>State Level</h5>';
            html += '<div class="fra-stats">';
            Object.entries(progress.state_level).slice(0, 5).forEach(([state, statuses]) => {
                const total = Object.values(statuses).reduce((a, b) => a + b, 0);
                html += `<div class="fra-stat">${state}: ${total}</div>`;
            });
            html += '</div></div>';
        }
        
        fraPanel.innerHTML = html || '<div class="loading">No FRA data available</div>';
    }
    
    updateFeatureCount(count) {
        const countElement = document.getElementById('feature-count');
        if (countElement) {
            countElement.textContent = `${count.toLocaleString()} features`;
        }
    }
    
    updateScaleDisplay() {
        const scaleElement = document.getElementById('map-scale');
        if (scaleElement) {
            const zoom = this.map.getZoom();
            const scale = Math.round(591657550 / Math.pow(2, zoom));
            scaleElement.textContent = `Scale: 1:${scale.toLocaleString()}`;
        }
    }
    
    async exportData() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`/api/export?${params}`);
            const data = await response.json();
            
            // Create and download file
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `india_land_use_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showError('Failed to export data');
        }
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    showError(message) {
        console.error(message);
        // You could add a toast notification here
    }
}

// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new IndiaLandUseMap();
});
