/**
 * Vanachitra.AI - Forest Rights Act WebGIS System
 * Advanced FRA spatial data visualization with realistic hierarchy
 */

class VanachitraFRAViewer {
    constructor() {
        this.map = null;
        this.fraData = null;
        this.filteredData = null;
        this.currentFeature = null;
        this.layers = {
            cfr: null,
            ifr: null,
            cr: null,
            agriculture: null,
            waterBody: null
        };
        this.colors = {
            CFR: { color: '#8B4513', fillColor: '#A0522D', fillOpacity: 0.4 },
            IFR: { color: '#FF6B35', fillColor: '#F7931E', fillOpacity: 0.6 },
            CR: { color: '#9B59B6', fillColor: '#8E44AD', fillOpacity: 0.6 },
            Agriculture: { color: '#2ECC71', fillColor: '#27AE60', fillOpacity: 0.7 },
            'Water Body': { color: '#3498DB', fillColor: '#2980B9', fillOpacity: 0.8 }
        };
        this.hierarchyVisible = true;
        this.labelsVisible = false;
        
        this.init();
    }

    async init() {
        this.showLoading(true);
        await this.initMap();
        await this.loadFRAData();
        this.setupEventListeners();
        this.setupFilters();
        this.updateStatistics();
        this.showLoading(false);
        
        console.log('🌳 Vanachitra.AI initialized successfully!');
    }

    async initMap() {
        // Initialize map centered on India with satellite imagery
        this.map = L.map('map', {
            center: [20.5937, 78.9629], // Center of India
            zoom: 5,
            minZoom: 4,
            maxZoom: 18,
            zoomControl: false
        });

        // Add Zoom Control to bottom right
        L.control.zoom({
            position: 'bottomright'
        }).addTo(this.map);

        // Base layers with satellite imagery
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '© Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community',
            maxZoom: 18
        });

        const topoLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
            attribution: '© Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), (c) OpenStreetMap contributors, and the GIS User Community',
            maxZoom: 18
        });

        const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        });

        // Add default satellite layer
        satelliteLayer.addTo(this.map);

        // Layer control
        const baseLayers = {
            "🛰️ Satellite": satelliteLayer,
            "🗺️ Topographic": topoLayer,
            "🏘️ Street Map": streetLayer
        };

        L.control.layers(baseLayers, null, {
            position: 'topleft',
            collapsed: false
        }).addTo(this.map);

        // Scale control
        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false
        }).addTo(this.map);
    }

    async loadFRAData() {
        try {
            const response = await fetch('/api/vanachitra_fra_data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.fraData = await response.json();
            this.filteredData = this.fraData;
            
            this.displayFRALayers();
            
            // Zoom to data bounds
            if (this.fraData.features && this.fraData.features.length > 0) {
                const group = new L.FeatureGroup();
                this.fraData.features.forEach(feature => {
                    if (feature.geometry) {
                        group.addLayer(L.geoJSON(feature));
                    }
                });
                
                if (group.getLayers().length > 0) {
                    this.map.fitBounds(group.getBounds(), { padding: [20, 20] });
                }
            }
            
        } catch (error) {
            console.error('❌ Error loading FRA data:', error);
            this.showAlert('Failed to load FRA data. Please check the server connection.', 'error');
        }
    }

    displayFRALayers() {
        // Clear existing layers
        Object.values(this.layers).forEach(layer => {
            if (layer && this.map.hasLayer(layer)) {
                this.map.removeLayer(layer);
            }
        });

        // Reset layers object
        this.layers = {
            cfr: null,
            ifr: null,
            cr: null,
            agriculture: null,
            waterBody: null
        };

        if (!this.filteredData || !this.filteredData.features) {
            console.warn('⚠️ No FRA data to display');
            return;
        }

        console.log(`Displaying ${this.filteredData.features.length} features`);

        // Group features by type - fix the field mapping
        const featureGroups = {
            'Community Forest Resource Rights': [],
            'Individual Forest Rights': [],
            'Community Rights': [],
            'Agriculture': [],
            'Water Body': []
        };

        this.filteredData.features.forEach(feature => {
            const fraType = feature.properties.fra_type || feature.properties.feature_type;
            if (featureGroups[fraType]) {
                featureGroups[fraType].push(feature);
            } else {
                // Handle legacy data format
                if (feature.properties.claim_type === 'CFR') {
                    featureGroups['Community Forest Resource Rights'].push(feature);
                } else if (feature.properties.claim_type === 'IFR') {
                    featureGroups['Individual Forest Rights'].push(feature);
                } else if (feature.properties.claim_type === 'CR') {
                    featureGroups['Community Rights'].push(feature);
                }
            }
        });

        // Create layers for each FRA type with proper hierarchy (CFR at bottom, others on top)
        const layerMapping = {
            'Community Forest Resource Rights': 'cfr',
            'Individual Forest Rights': 'ifr', 
            'Community Rights': 'cr',
            'Agriculture': 'agriculture',
            'Water Body': 'waterBody'
        };

        const layerOrder = ['Community Forest Resource Rights', 'Agriculture', 'Water Body', 'Community Rights', 'Individual Forest Rights'];
        
        layerOrder.forEach(fraType => {
            if (featureGroups[fraType].length > 0) {
                const layerKey = layerMapping[fraType];
                this.layers[layerKey] = L.geoJSON(featureGroups[fraType], {
                    style: (feature) => this.getFeatureStyle(feature),
                    onEachFeature: (feature, layer) => this.onEachFeature(feature, layer)
                }).addTo(this.map);
                
                console.log(`Added ${fraType} layer with ${featureGroups[fraType].length} features`);
            }
        });

        // Add layer control for FRA layers
        this.addFRALayerControl();
    }

    getFeatureStyle(feature) {
        const fraType = feature.properties.fra_type || feature.properties.feature_type;
        let styleKey = fraType;
        
        // Map the actual data types to our color scheme
        if (feature.properties.claim_type === 'CFR' || fraType === 'Community Forest Resource Rights') {
            styleKey = 'CFR';
        } else if (feature.properties.claim_type === 'IFR' || fraType === 'Individual Forest Rights') {
            styleKey = 'IFR';
        } else if (feature.properties.claim_type === 'CR' || fraType === 'Community Rights') {
            styleKey = 'CR';
        } else if (fraType === 'Agriculture') {
            styleKey = 'Agriculture';
        } else if (fraType === 'Water Body') {
            styleKey = 'Water Body';
        }

        const baseStyle = this.colors[styleKey] || {
            color: '#333333',
            fillColor: '#666666',
            fillOpacity: 0.5
        };

        return {
            ...baseStyle,
            weight: styleKey === 'CFR' ? 3 : 2,
            opacity: 0.8,
            dashArray: feature.properties.status === 'Pending' ? '5, 5' : null
        };
    }

    onEachFeature(feature, layer) {
        // Create popup content
        const props = feature.properties;
        const popupContent = this.createPopupContent(props);
        layer.bindPopup(popupContent, {
            maxWidth: 400,
            className: 'custom-popup'
        });

        // Add click event
        layer.on('click', (e) => {
            this.highlightFeature(e.target);
            this.updateInfoPanel(props);
        });

        // Add hover events
        layer.on('mouseover', (e) => {
            const layer = e.target;
            layer.setStyle({
                weight: 4,
                opacity: 1,
                fillOpacity: 0.8
            });
        });

        layer.on('mouseout', (e) => {
            const layer = e.target;
            layer.setStyle(this.getFeatureStyle(feature));
        });

        // Add label if enabled
        if (this.labelsVisible) {
            this.addFeatureLabel(layer, props);
        }
    }

    createPopupContent(props) {
        const statusIcon = {
            'Approved': '✅',
            'Pending': '⏳',
            'Under Review': '🔄'
        }[props.status] || '❓';

        // Determine type and icon based on actual data structure
        let fraType = props.fra_type || props.feature_type;
        let fraId = props.claim_id || props.feature_id;
        
        const typeIcon = {
            'Community Forest Resource Rights': '🌲',
            'Individual Forest Rights': '🏠',
            'Community Rights': '🤝',
            'Agriculture': '🌾',
            'Water Body': '💧'
        }[fraType] || '📍';

        // Handle legacy data
        if (props.claim_type === 'CFR') {
            fraType = 'Community Forest Resource Rights';
        } else if (props.claim_type === 'IFR') {
            fraType = 'Individual Forest Rights';  
        } else if (props.claim_type === 'CR') {
            fraType = 'Community Rights';
        }

        return `
            <div class="popup-content">
                <h4>${typeIcon} ${fraType}</h4>
                <div class="popup-row">
                    <strong>ID:</strong> ${fraId}
                </div>
                <div class="popup-row">
                    <strong>Status:</strong> ${statusIcon} ${props.status || 'N/A'}
                </div>
                <div class="popup-row">
                    <strong>Area:</strong> ${(props.area_claimed || props.area_hectares || 0).toFixed(2)} hectares
                </div>
                <div class="popup-row">
                    <strong>Location:</strong> ${props.village}, ${props.district}, ${props.state}
                </div>
                ${props.total_households ? `
                <div class="popup-row">
                    <strong>Households:</strong> ${props.total_households}
                </div>
                ` : ''}
                ${props.beneficiary_households ? `
                <div class="popup-row">
                    <strong>Beneficiaries:</strong> ${props.beneficiary_households}
                </div>
                ` : ''}
                ${props.household_head ? `
                <div class="popup-row">
                    <strong>Household Head:</strong> ${props.household_head}
                </div>
                ` : ''}
                ${props.gram_sabha ? `
                <div class="popup-row">
                    <strong>Gram Sabha:</strong> ${props.gram_sabha}
                </div>
                ` : ''}
                ${props.tribal_community ? `
                <div class="popup-row">
                    <strong>Community:</strong> ${props.tribal_community}
                </div>
                ` : ''}
                <div class="popup-row">
                    <strong>Submission:</strong> ${props.submission_date || 'N/A'}
                </div>
            </div>
        `;
    }

    addFeatureLabel(layer, props) {
        const center = layer.getBounds().getCenter();
        const icon = L.divIcon({
            className: 'feature-label',
            html: `<div class="label-content">${props.fra_id}</div>`,
            iconSize: [60, 20],
            iconAnchor: [30, 10]
        });
        
        const marker = L.marker(center, { icon }).addTo(this.map);
        
        // Store reference for cleanup
        if (!layer._labelMarker) {
            layer._labelMarker = marker;
        }
    }

    addFRALayerControl() {
        // Create overlay layers control
        const overlayLayers = {};
        
        Object.entries(this.layers).forEach(([key, layer]) => {
            if (layer) {
                const displayName = {
                    'cfr': '🌲 CFR - Community Forest Resource Rights',
                    'ifr': '🏠 IFR - Individual Forest Rights',
                    'cr': '🤝 CR - Community Rights',
                    'agriculture': '🌾 Agriculture',
                    'waterBody': '💧 Water Bodies'
                }[key] || key;
                
                overlayLayers[displayName] = layer;
            }
        });

        if (Object.keys(overlayLayers).length > 0) {
            // Remove existing layer control if it exists
            this.map.eachLayer(layer => {
                if (layer instanceof L.Control.Layers) {
                    this.map.removeControl(layer);
                }
            });

            L.control.layers(null, overlayLayers, {
                position: 'topright',
                collapsed: false
            }).addTo(this.map);
        }
    }

    highlightFeature(targetLayer) {
        // Reset previous highlight
        if (this.currentFeature) {
            this.currentFeature.setStyle(this.getFeatureStyle(this.currentFeature.feature));
        }

        // Highlight current feature
        this.currentFeature = targetLayer;
        targetLayer.setStyle({
            weight: 5,
            color: '#ffff00',
            opacity: 1,
            fillOpacity: 0.9
        });
    }

    updateInfoPanel(properties) {
        // Info panel removed - just show popup instead
        console.log('Feature selected:', properties);
    }

    setupEventListeners() {
        // Filter buttons
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });

        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });

        // Action buttons
        document.getElementById('zoom-to-data').addEventListener('click', () => {
            this.zoomToData();
        });

        document.getElementById('export-data').addEventListener('click', () => {
            this.exportData();
        });

        document.getElementById('show-hierarchy').addEventListener('click', () => {
            this.toggleHierarchy();
        });

        document.getElementById('toggle-labels').addEventListener('click', () => {
            this.toggleLabels();
        });

        // Map control buttons
        document.getElementById('fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        document.getElementById('reset-view').addEventListener('click', () => {
            this.resetView();
        });

        document.getElementById('layer-toggle').addEventListener('click', () => {
            this.toggleAllLayers();
        });

        // Filter cascading
        document.getElementById('state-filter').addEventListener('change', () => {
            this.updateDistrictFilter();
        });

        document.getElementById('district-filter').addEventListener('change', () => {
            this.updateVillageFilter();
        });
    }

    setupFilters() {
        if (!this.fraData || !this.fraData.features) return;

        // Get unique values for filters
        const states = [...new Set(this.fraData.features.map(f => f.properties.state))].sort();
        
        // Populate state filter
        const stateFilter = document.getElementById('state-filter');
        stateFilter.innerHTML = '<option value="">All States</option>';
        states.forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateFilter.appendChild(option);
        });

        console.log('Filter setup complete. Available states:', states);
    }

    updateDistrictFilter() {
        const selectedState = document.getElementById('state-filter').value;
        const districtFilter = document.getElementById('district-filter');
        
        // Clear existing options
        districtFilter.innerHTML = '<option value="">All Districts</option>';
        
        if (!selectedState) return;

        const districts = [...new Set(
            this.fraData.features
                .filter(f => f.properties.state === selectedState)
                .map(f => f.properties.district)
        )].sort();

        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            districtFilter.appendChild(option);
        });
    }

    updateVillageFilter() {
        const selectedState = document.getElementById('state-filter').value;
        const selectedDistrict = document.getElementById('district-filter').value;
        const villageFilter = document.getElementById('village-filter');
        
        // Clear existing options
        villageFilter.innerHTML = '<option value="">All Villages</option>';
        
        if (!selectedState || !selectedDistrict) return;

        const villages = [...new Set(
            this.fraData.features
                .filter(f => f.properties.state === selectedState && f.properties.district === selectedDistrict)
                .map(f => f.properties.village)
        )].sort();

        villages.forEach(village => {
            const option = document.createElement('option');
            option.value = village;
            option.textContent = village;
            villageFilter.appendChild(option);
        });
    }

    applyFilters() {
        if (!this.fraData) {
            this.showAlert('No data available to filter!', 'error');
            return;
        }

        const filters = {
            state: document.getElementById('state-filter').value,
            district: document.getElementById('district-filter').value,
            village: document.getElementById('village-filter').value,
            fraType: document.getElementById('fra-type-filter').value,
            status: document.getElementById('status-filter').value
        };

        console.log('Applying filters:', filters);

        // Filter the data
        const originalCount = this.fraData.features.length;
        this.filteredData = {
            ...this.fraData,
            features: this.fraData.features.filter(feature => {
                const props = feature.properties;
                
                // Apply each filter if it has a value
                if (filters.state && props.state !== filters.state) return false;
                if (filters.district && props.district !== filters.district) return false;
                if (filters.village && props.village !== filters.village) return false;
                
                // Handle FRA type filtering with proper field mapping
                if (filters.fraType) {
                    const fraType = props.fra_type || props.feature_type;
                    let matches = false;
                    
                    if (filters.fraType === 'Community Forest Resource Rights' && 
                        (props.claim_type === 'CFR' || fraType === 'Community Forest Resource Rights')) {
                        matches = true;
                    } else if (filters.fraType === 'Individual Forest Rights' && 
                               (props.claim_type === 'IFR' || fraType === 'Individual Forest Rights')) {
                        matches = true;
                    } else if (filters.fraType === 'Community Rights' && 
                               (props.claim_type === 'CR' || fraType === 'Community Rights')) {
                        matches = true;
                    } else if (filters.fraType === fraType) {
                        matches = true;
                    }
                    
                    if (!matches) return false;
                }
                
                if (filters.status && props.status !== filters.status) return false;
                
                return true;
            })
        };

        const filteredCount = this.filteredData.features.length;
        console.log(`Filtered from ${originalCount} to ${filteredCount} features`);

        // Redisplay the layers with filtered data
        this.displayFRALayers();
        this.updateStatistics();
        
        // Zoom to filtered data if available
        if (filteredCount > 0) {
            this.zoomToData();
        }
        
        this.showAlert(`Filters applied! Showing ${filteredCount} of ${originalCount} features.`, 'success');
    }

    clearFilters() {
        // Reset all filter dropdowns
        document.getElementById('state-filter').value = '';
        document.getElementById('district-filter').value = '';
        document.getElementById('village-filter').value = '';
        document.getElementById('fra-type-filter').value = '';
        document.getElementById('status-filter').value = '';

        // Reset district and village filters
        document.getElementById('district-filter').innerHTML = '<option value="">All Districts</option>';
        document.getElementById('village-filter').innerHTML = '<option value="">All Villages</option>';

        // Reset filtered data
        this.filteredData = this.fraData;
        this.displayFRALayers();
        this.updateStatistics();
        this.showAlert('Filters cleared!', 'success');
    }

    updateStatistics() {
        if (!this.filteredData || !this.filteredData.features) return;

        const features = this.filteredData.features;
        
        // Count by type - handle both data formats
        const typeCounts = {
            CFR: 0,
            IFR: 0,
            CR: 0,
            Agriculture: 0,
            'Water Body': 0
        };

        let totalArea = 0;
        let approvedCount = 0;
        let pendingCount = 0;

        features.forEach(feature => {
            const props = feature.properties;
            
            // Count by type - handle different field names
            let fraType = props.fra_type || props.feature_type;
            if (props.claim_type === 'CFR' || fraType === 'Community Forest Resource Rights') {
                typeCounts.CFR++;
            } else if (props.claim_type === 'IFR' || fraType === 'Individual Forest Rights') {
                typeCounts.IFR++;
            } else if (props.claim_type === 'CR' || fraType === 'Community Rights') {
                typeCounts.CR++;
            } else if (fraType === 'Agriculture') {
                typeCounts.Agriculture++;
            } else if (fraType === 'Water Body') {
                typeCounts['Water Body']++;
            }

            // Calculate area - handle different field names
            totalArea += props.area_claimed || props.area_hectares || 0;

            // Count by status
            if (props.status === 'Approved') {
                approvedCount++;
            } else if (props.status === 'Pending') {
                pendingCount++;
            }
        });

        // Update UI
        document.getElementById('cfr-count').textContent = typeCounts.CFR;
        document.getElementById('ifr-count').textContent = typeCounts.IFR;
        document.getElementById('cr-count').textContent = typeCounts.CR;
        
        document.getElementById('total-features').textContent = features.length;
        document.getElementById('total-area').textContent = totalArea.toFixed(1);
        document.getElementById('approved-claims').textContent = approvedCount;
        document.getElementById('pending-claims').textContent = pendingCount;

        console.log('Statistics updated:', {
            total: features.length,
            cfr: typeCounts.CFR,
            ifr: typeCounts.IFR,
            cr: typeCounts.CR,
            agriculture: typeCounts.Agriculture,
            waterBody: typeCounts['Water Body']
        });
    }

    zoomToData() {
        if (!this.filteredData || !this.filteredData.features.length) {
            this.showAlert('No data to zoom to!', 'error');
            return;
        }

        const group = new L.FeatureGroup();
        this.filteredData.features.forEach(feature => {
            if (feature.geometry) {
                group.addLayer(L.geoJSON(feature));
            }
        });
        
        if (group.getLayers().length > 0) {
            this.map.fitBounds(group.getBounds(), { padding: [20, 20] });
        }
    }

    exportData() {
        if (!this.filteredData) {
            this.showAlert('No data to export!', 'error');
            return;
        }

        const dataStr = JSON.stringify(this.filteredData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `vanachitra_fra_data_${new Date().toISOString().split('T')[0]}.geojson`;
        link.click();
        
        this.showAlert('Data exported successfully!', 'success');
    }

    toggleHierarchy() {
        this.hierarchyVisible = !this.hierarchyVisible;
        
        if (this.hierarchyVisible) {
            this.displayFRALayers();
            document.getElementById('show-hierarchy').textContent = '🔗 Hide Hierarchy';
        } else {
            // Show all layers without hierarchy
            document.getElementById('show-hierarchy').textContent = '🏗️ Show Hierarchy';
        }
    }

    toggleLabels() {
        this.labelsVisible = !this.labelsVisible;
        
        // Remove existing labels
        this.map.eachLayer(layer => {
            if (layer._labelMarker) {
                this.map.removeLayer(layer._labelMarker);
                delete layer._labelMarker;
            }
        });

        if (this.labelsVisible) {
            // Add labels to all visible features
            Object.values(this.layers).forEach(layerGroup => {
                if (layerGroup && this.map.hasLayer(layerGroup)) {
                    layerGroup.eachLayer(layer => {
                        if (layer.feature && layer.feature.properties) {
                            this.addFeatureLabel(layer, layer.feature.properties);
                        }
                    });
                }
            });
            document.getElementById('toggle-labels').textContent = '🚫 Hide Labels';
        } else {
            document.getElementById('toggle-labels').textContent = '🏷️ Show Labels';
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    resetView() {
        this.map.setView([20.5937, 78.9629], 5);
        
        // Clear any highlights
        if (this.currentFeature) {
            this.currentFeature.setStyle(this.getFeatureStyle(this.currentFeature.feature));
            this.currentFeature = null;
        }
    }

    toggleAllLayers() {
        const hasVisibleLayers = Object.values(this.layers).some(layer => 
            layer && this.map.hasLayer(layer)
        );

        Object.values(this.layers).forEach(layer => {
            if (layer) {
                if (hasVisibleLayers) {
                    this.map.removeLayer(layer);
                } else {
                    this.map.addLayer(layer);
                }
            }
        });
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = type === 'error' ? 'alert' : 'success';
        alertDiv.textContent = message;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}

// Initialize Vanachitra.AI when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.vanachitraViewer = new VanachitraFRAViewer();
});

// CSS for popup and labels
const style = document.createElement('style');
style.textContent = `
    .custom-popup .leaflet-popup-content {
        margin: 0;
        padding: 0;
    }
    
    .popup-content {
        padding: 15px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .popup-content h4 {
        margin: 0 0 10px 0;
        color: #2d5016;
        border-bottom: 2px solid #6fa824;
        padding-bottom: 5px;
    }
    
    .popup-row {
        margin-bottom: 5px;
        padding: 2px 0;
    }
    
    .popup-row strong {
        color: #4a7c1c;
    }
    
    .feature-label {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #333;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        text-align: center;
        pointer-events: none;
    }
    
    .label-content {
        padding: 2px 4px;
        color: #2d5016;
    }
`;
document.head.appendChild(style);