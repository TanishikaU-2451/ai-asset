/**
 * India Asset Management - 3-Layer WebGIS System
 * Focused on Indian territories with satellite-based mapping
 */

class IndiaWebGIS {
    constructor() {
        this.map = null;
        this.layers = {
            assets: null,
            fra: null,
            admin: null,
            baseLayers: {}
        };
        this.currentFilters = {};
        this.data = {
            assets: null,
            fra: null,
            admin: null
        };
        this.selectedFeatures = new Set();
        
        // India bounding box
        this.indiaBounds = [[6.0, 68.0], [37.0, 97.0]];
        this.indiaCenter = [22.9734, 78.6569];
        
        // Asset type styles with realistic colors
        this.assetStyles = {
            'water': { 
                color: '#1f77b4', 
                fillColor: '#1f77b4', 
                fillOpacity: 0.8, 
                weight: 1.5 
            },
            'forest': { 
                color: '#2ca02c', 
                fillColor: '#2ca02c', 
                fillOpacity: 0.7, 
                weight: 1.5 
            },
            'agricultural': { 
                color: '#ff7f0e', 
                fillColor: '#ff7f0e', 
                fillOpacity: 0.6, 
                weight: 1.5 
            },
            'homestead': { 
                color: '#d62728', 
                fillColor: '#d62728', 
                fillOpacity: 0.7, 
                weight: 1.5 
            }
        };
        
        // FRA type styles
        this.fraStyles = {
            'IFR': { 
                color: '#8c564b', 
                fillColor: '#8c564b', 
                fillOpacity: 0.5, 
                weight: 2,
                dashArray: '5, 5'
            },
            'CFR': { 
                color: '#e377c2', 
                fillColor: '#e377c2', 
                fillOpacity: 0.5, 
                weight: 2,
                dashArray: '10, 5'
            },
            'CR': { 
                color: '#bcbd22', 
                fillColor: '#bcbd22', 
                fillOpacity: 0.5, 
                weight: 2,
                dashArray: '15, 5, 5, 5'
            }
        };
        
        // Administrative boundary styles
        this.adminStyles = {
            state: {
                color: '#2c3e50',
                weight: 3,
                fillOpacity: 0,
                dashArray: '20, 10'
            },
            district: {
                color: '#34495e',
                weight: 2,
                fillOpacity: 0,
                dashArray: '10, 5'
            },
            village: {
                color: '#7f8c8d',
                weight: 1,
                fillOpacity: 0,
                dashArray: '5, 3'
            },
            highlighted: {
                color: '#e74c3c',
                weight: 4,
                fillOpacity: 0.2,
                fillColor: '#e74c3c'
            }
        };
        
        this.init();
    }
    
    async init() {
        this.showLoading(true);
        this.initializeMap();
        this.setupEventListeners();
        this.setupOpacityControls();
        await this.loadData();
        this.setupLegend();
        this.showLoading(false);
    }
    
    initializeMap() {
        // Initialize map centered on India with restricted bounds
        this.map = L.map('map', {
            center: this.indiaCenter,
            zoom: 5,
            minZoom: 4,
            maxZoom: 18,
            maxBounds: this.indiaBounds,
            maxBoundsViscosity: 1.0
        });
        
        // Satellite base layer (using multiple providers for better coverage)
        const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Imagery &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
            name: 'Satellite'
        });
        
        // OpenStreetMap layer for reference
        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name: 'OpenStreetMap'
        });
        
        // Terrain layer
        const terrainLayer = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png', {
            attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name: 'Terrain'
        });
        
        // Add satellite as default
        satelliteLayer.addTo(this.map);
        
        // Store base layers
        this.layers.baseLayers = {
            'Satellite': satelliteLayer,
            'OpenStreetMap': osmLayer,
            'Terrain': terrainLayer
        };
        
        // Add layer control
        L.control.layers(this.layers.baseLayers).addTo(this.map);
        
        // Add scale control
        L.control.scale({
            position: 'bottomright',
            metric: true,
            imperial: false
        }).addTo(this.map);
        
        // Add coordinate display
        this.map.on('mousemove', (e) => {
            this.updateCoordinateDisplay(e.latlng);
        });
        
        // Add click handler for feature selection
        this.map.on('click', (e) => {
            this.handleMapClick(e);
        });
        
        // Add zoom change handler for statistics
        this.map.on('zoomend', () => {
            this.updateZoomStatistic();
        });
    }
    
    setupEventListeners() {
        // Layer toggles
        document.getElementById('assets-layer').addEventListener('change', (e) => {
            this.toggleLayer('assets', e.target.checked);
        });
        
        document.getElementById('fra-layer').addEventListener('change', (e) => {
            this.toggleLayer('fra', e.target.checked);
        });
        
        document.getElementById('admin-layer').addEventListener('change', (e) => {
            this.toggleLayer('admin', e.target.checked);
        });
        
        // Opacity controls
        document.getElementById('assets-opacity').addEventListener('input', (e) => {
            this.updateLayerOpacity('assets', parseFloat(e.target.value));
        });
        
        document.getElementById('fra-opacity').addEventListener('input', (e) => {
            this.updateLayerOpacity('fra', parseFloat(e.target.value));
        });
        
        document.getElementById('admin-opacity').addEventListener('input', (e) => {
            this.updateLayerOpacity('admin', parseFloat(e.target.value));
        });
        
        // Filter controls
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });
        
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Geographic filter cascading
        document.getElementById('state-filter').addEventListener('change', (e) => {
            this.updateDistrictOptions(e.target.value);
        });
        
        document.getElementById('district-filter').addEventListener('change', (e) => {
            this.updateVillageOptions(e.target.value);
        });
        
        // Map controls
        document.getElementById('reset-view').addEventListener('click', () => {
            this.resetView();
        });
        
        document.getElementById('zoom-india').addEventListener('click', () => {
            this.zoomToIndia();
        });
        
        document.getElementById('toggle-satellite').addEventListener('click', () => {
            this.toggleBasemap();
        });
        
        document.getElementById('fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });
    }
    
    async loadData() {
        try {
            // Load assets data
            const assetsResponse = await fetch('/api/assets');
            this.data.assets = await assetsResponse.json();
            
            // Load FRA claims data
            const fraResponse = await fetch('/api/fra-claims');
            this.data.fra = await fraResponse.json();
            
            // Generate administrative boundaries (since we don't have real data)
            this.data.admin = await this.generateAdminBoundaries();
            
            // Create layers
            this.createAssetLayer();
            this.createFRALayer();
            this.createAdminLayer();
            
            // Populate filter options
            this.populateFilterOptions();
            
            // Update statistics
            this.updateStatistics();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load map data. Please refresh the page.');
        }
    }
    
    createAssetLayer() {
        if (!this.data.assets || !this.data.assets.features) return;
        
        this.layers.assets = L.geoJSON(this.data.assets, {
            style: (feature) => {
                const assetType = feature.properties.class || 'agricultural';
                return this.assetStyles[assetType] || this.assetStyles.agricultural;
            },
            onEachFeature: (feature, layer) => {
                // Add hover effects
                layer.on({
                    mouseover: (e) => this.highlightFeature(e),
                    mouseout: (e) => this.resetHighlight(e),
                    click: (e) => this.selectFeature(e)
                });
                
                // Add popup with asset information
                const props = feature.properties;
                const popupContent = `
                    <div class="popup-content">
                        <h4>Asset Information</h4>
                        <p><strong>Type:</strong> ${props.class || 'Unknown'}</p>
                        <p><strong>Area:</strong> ${props.area_km2 || 'N/A'} km²</p>
                        <p><strong>Confidence:</strong> ${props.confidence ? (props.confidence * 100).toFixed(1) + '%' : 'N/A'}</p>
                    </div>
                `;
                layer.bindPopup(popupContent);
            }
        });
        
        this.layers.assets.addTo(this.map);
    }
    
    createFRALayer() {
        if (!this.data.fra || !this.data.fra.features) return;
        
        this.layers.fra = L.geoJSON(this.data.fra, {
            style: (feature) => {
                const fraType = feature.properties.fra_type || 'IFR';
                return this.fraStyles[fraType] || this.fraStyles.IFR;
            },
            onEachFeature: (feature, layer) => {
                // Add hover effects
                layer.on({
                    mouseover: (e) => this.highlightFeature(e),
                    mouseout: (e) => this.resetHighlight(e),
                    click: (e) => this.selectFeature(e)
                });
                
                // Add popup with FRA information
                const props = feature.properties;
                const popupContent = `
                    <div class="popup-content">
                        <h4>FRA Claim Information</h4>
                        <p><strong>Claim ID:</strong> ${props.claim_id || 'N/A'}</p>
                        <p><strong>Type:</strong> ${props.fra_type_name || props.fra_type || 'N/A'}</p>
                        <p><strong>State:</strong> ${props.state || 'N/A'}</p>
                        <p><strong>District:</strong> ${props.district || 'N/A'}</p>
                        <p><strong>Village:</strong> ${props.village || 'N/A'}</p>
                        <p><strong>Area:</strong> ${props.claim_area_ha || 'N/A'} hectares</p>
                        <p><strong>Status:</strong> ${props.status_name || props.status || 'N/A'}</p>
                        <p><strong>Community:</strong> ${props.tribal_community || 'N/A'}</p>
                    </div>
                `;
                layer.bindPopup(popupContent);
            }
        });
        
        this.layers.fra.addTo(this.map);
    }
    
    createAdminLayer() {
        if (!this.data.admin || !this.data.admin.features) return;
        
        this.layers.admin = L.geoJSON(this.data.admin, {
            style: (feature) => {
                const adminLevel = feature.properties.admin_level || 'state';
                return this.adminStyles[adminLevel] || this.adminStyles.state;
            },
            onEachFeature: (feature, layer) => {
                // Add hover effects for boundary highlighting
                layer.on({
                    mouseover: (e) => this.highlightBoundary(e),
                    mouseout: (e) => this.resetBoundaryHighlight(e),
                    click: (e) => this.selectBoundary(e)
                });
                
                // Add popup with administrative information
                const props = feature.properties;
                const popupContent = `
                    <div class="popup-content">
                        <h4>Administrative Boundary</h4>
                        <p><strong>Level:</strong> ${props.admin_level || 'N/A'}</p>
                        <p><strong>Name:</strong> ${props.name || 'N/A'}</p>
                        <p><strong>Code:</strong> ${props.code || 'N/A'}</p>
                    </div>
                `;
                layer.bindPopup(popupContent);
            }
        });
        
        this.layers.admin.addTo(this.map);
    }
    
    async generateAdminBoundaries() {
        // Generate realistic administrative boundaries for Indian states/districts/villages
        // This is a simplified version - in production, use real boundary data
        
        const features = [];
        const states = [
            'Andhra Pradesh', 'Assam', 'Chhattisgarh', 'Gujarat', 'Jharkhand',
            'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Odisha',
            'Rajasthan', 'Telangana', 'West Bengal'
        ];
        
        // Generate state boundaries (simplified rectangles within India bounds)
        for (let i = 0; i < states.length; i++) {
            const state = states[i];
            const latOffset = (i % 4) * 3;
            const lonOffset = Math.floor(i / 4) * 5;
            
            const bounds = [
                [20 + latOffset, 75 + lonOffset],
                [20 + latOffset, 80 + lonOffset],
                [25 + latOffset, 80 + lonOffset],
                [25 + latOffset, 75 + lonOffset],
                [20 + latOffset, 75 + lonOffset]
            ];
            
            features.push({
                type: 'Feature',
                properties: {
                    admin_level: 'state',
                    name: state,
                    code: `ST_${i + 1}`
                },
                geometry: {
                    type: 'Polygon',
                    coordinates: [bounds]
                }
            });
        }
        
        return {
            type: 'FeatureCollection',
            features: features
        };
    }
    
    populateFilterOptions() {
        // Populate state filter
        const stateFilter = document.getElementById('state-filter');
        const states = [...new Set(this.data.fra.features.map(f => f.properties.state))].sort();
        
        states.forEach(state => {
            if (state) {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                stateFilter.appendChild(option);
            }
        });
    }
    
    updateDistrictOptions(selectedState) {
        const districtFilter = document.getElementById('district-filter');
        districtFilter.innerHTML = '<option value="">All Districts</option>';
        
        if (selectedState) {
            const districts = [...new Set(
                this.data.fra.features
                    .filter(f => f.properties.state === selectedState)
                    .map(f => f.properties.district)
            )].sort();
            
            districts.forEach(district => {
                if (district) {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    districtFilter.appendChild(option);
                }
            });
        }
    }
    
    updateVillageOptions(selectedDistrict) {
        const villageFilter = document.getElementById('village-filter');
        villageFilter.innerHTML = '<option value="">All Villages</option>';
        
        if (selectedDistrict) {
            const villages = [...new Set(
                this.data.fra.features
                    .filter(f => f.properties.district === selectedDistrict)
                    .map(f => f.properties.village)
            )].sort();
            
            villages.forEach(village => {
                if (village) {
                    const option = document.createElement('option');
                    option.value = village;
                    option.textContent = village;
                    villageFilter.appendChild(option);
                }
            });
        }
    }
    
    applyFilters() {
        this.currentFilters = {
            assetType: document.getElementById('asset-type-filter').value,
            minArea: parseFloat(document.getElementById('min-area-filter').value) || 0,
            state: document.getElementById('state-filter').value,
            district: document.getElementById('district-filter').value,
            village: document.getElementById('village-filter').value,
            fraType: document.getElementById('fra-type-filter').value,
            status: document.getElementById('status-filter').value
        };
        
        this.updateLayerVisibility();
        this.highlightSelectedBoundaries();
    }
    
    updateLayerVisibility() {
        // Filter assets layer
        if (this.layers.assets) {
            this.layers.assets.eachLayer(layer => {
                const props = layer.feature.properties;
                let visible = true;
                
                if (this.currentFilters.assetType && props.class !== this.currentFilters.assetType) {
                    visible = false;
                }
                
                if (this.currentFilters.minArea && (props.area_km2 || 0) < this.currentFilters.minArea) {
                    visible = false;
                }
                
                layer.setStyle({ opacity: visible ? 1 : 0, fillOpacity: visible ? 0.8 : 0 });
            });
        }
        
        // Filter FRA layer
        if (this.layers.fra) {
            this.layers.fra.eachLayer(layer => {
                const props = layer.feature.properties;
                let visible = true;
                
                if (this.currentFilters.state && props.state !== this.currentFilters.state) {
                    visible = false;
                }
                
                if (this.currentFilters.district && props.district !== this.currentFilters.district) {
                    visible = false;
                }
                
                if (this.currentFilters.village && props.village !== this.currentFilters.village) {
                    visible = false;
                }
                
                if (this.currentFilters.fraType && props.fra_type !== this.currentFilters.fraType) {
                    visible = false;
                }
                
                if (this.currentFilters.status && props.status !== this.currentFilters.status) {
                    visible = false;
                }
                
                layer.setStyle({ opacity: visible ? 1 : 0, fillOpacity: visible ? 0.5 : 0 });
            });
        }
    }
    
    highlightSelectedBoundaries() {
        if (!this.layers.admin) return;
        
        this.layers.admin.eachLayer(layer => {
            const props = layer.feature.properties;
            let highlighted = false;
            
            // Highlight based on selected filters
            if (this.currentFilters.state && props.name === this.currentFilters.state) {
                highlighted = true;
            }
            
            if (highlighted) {
                layer.setStyle(this.adminStyles.highlighted);
            } else {
                const adminLevel = props.admin_level || 'state';
                layer.setStyle(this.adminStyles[adminLevel]);
            }
        });
    }
    
    clearFilters() {
        // Reset all filter controls
        document.getElementById('asset-type-filter').value = '';
        document.getElementById('min-area-filter').value = '';
        document.getElementById('state-filter').value = '';
        document.getElementById('district-filter').value = '';
        document.getElementById('village-filter').value = '';
        document.getElementById('fra-type-filter').value = '';
        document.getElementById('status-filter').value = '';
        
        // Clear current filters
        this.currentFilters = {};
        
        // Reset layer visibility
        this.updateLayerVisibility();
        this.highlightSelectedBoundaries();
        
        // Update dependent dropdowns
        this.updateDistrictOptions('');
        this.updateVillageOptions('');
    }
    
    toggleLayer(layerName, visible) {
        if (this.layers[layerName]) {
            if (visible) {
                this.layers[layerName].addTo(this.map);
            } else {
                this.map.removeLayer(this.layers[layerName]);
            }
        }
    }
    
    updateLayerOpacity(layerName, opacity) {
        if (this.layers[layerName]) {
            this.layers[layerName].setStyle({ fillOpacity: opacity, opacity: opacity });
        }
    }
    
    highlightFeature(e) {
        const layer = e.target;
        layer.setStyle({
            weight: 3,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.9
        });
        
        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
            layer.bringToFront();
        }
    }
    
    resetHighlight(e) {
        // Reset to original style based on feature type
        const feature = e.target.feature;
        if (feature.properties.class) {
            // Asset feature
            const assetType = feature.properties.class;
            e.target.setStyle(this.assetStyles[assetType] || this.assetStyles.agricultural);
        } else if (feature.properties.fra_type) {
            // FRA feature
            const fraType = feature.properties.fra_type;
            e.target.setStyle(this.fraStyles[fraType] || this.fraStyles.IFR);
        }
    }
    
    highlightBoundary(e) {
        const layer = e.target;
        layer.setStyle({
            weight: 4,
            color: '#e74c3c',
            fillOpacity: 0.1,
            fillColor: '#e74c3c'
        });
    }
    
    resetBoundaryHighlight(e) {
        const feature = e.target.feature;
        const adminLevel = feature.properties.admin_level || 'state';
        e.target.setStyle(this.adminStyles[adminLevel]);
    }
    
    selectFeature(e) {
        const feature = e.target.feature;
        this.updateInfoPanel(feature);
        
        // Zoom to feature if it's small
        const bounds = e.target.getBounds();
        if (bounds.isValid()) {
            this.map.fitBounds(bounds, { padding: [20, 20] });
        }
    }
    
    selectBoundary(e) {
        const feature = e.target.feature;
        this.updateInfoPanel(feature);
        
        // Zoom to boundary
        const bounds = e.target.getBounds();
        if (bounds.isValid()) {
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    }
    
    updateInfoPanel(feature) {
        const infoDiv = document.getElementById('feature-info');
        const props = feature.properties;
        
        let content = '<h4>Feature Details</h4>';
        
        if (props.class) {
            // Asset feature
            content += `
                <p><strong>Type:</strong> ${props.class}</p>
                <p><strong>Area:</strong> ${props.area_km2 || 'N/A'} km²</p>
                <p><strong>Confidence:</strong> ${props.confidence ? (props.confidence * 100).toFixed(1) + '%' : 'N/A'}</p>
            `;
        } else if (props.fra_type) {
            // FRA feature
            content += `
                <p><strong>Claim ID:</strong> ${props.claim_id || 'N/A'}</p>
                <p><strong>Type:</strong> ${props.fra_type_name || props.fra_type}</p>
                <p><strong>State:</strong> ${props.state || 'N/A'}</p>
                <p><strong>District:</strong> ${props.district || 'N/A'}</p>
                <p><strong>Status:</strong> ${props.status_name || props.status}</p>
            `;
        } else if (props.admin_level) {
            // Administrative boundary
            content += `
                <p><strong>Level:</strong> ${props.admin_level}</p>
                <p><strong>Name:</strong> ${props.name || 'N/A'}</p>
                <p><strong>Code:</strong> ${props.code || 'N/A'}</p>
            `;
        }
        
        infoDiv.innerHTML = content;
    }
    
    updateCoordinateDisplay(latlng) {
        // You can add a coordinate display element if needed
    }
    
    handleMapClick(e) {
        // Handle general map clicks
    }
    
    resetView() {
        this.map.setView(this.indiaCenter, 5);
    }
    
    zoomToIndia() {
        this.map.fitBounds(this.indiaBounds, { padding: [20, 20] });
    }
    
    toggleBasemap() {
        // Cycle through base layers
        const layerNames = Object.keys(this.layers.baseLayers);
        let currentIndex = 0;
        
        // Find current layer
        for (let i = 0; i < layerNames.length; i++) {
            if (this.map.hasLayer(this.layers.baseLayers[layerNames[i]])) {
                currentIndex = i;
                break;
            }
        }
        
        // Switch to next layer
        const nextIndex = (currentIndex + 1) % layerNames.length;
        const currentLayer = this.layers.baseLayers[layerNames[currentIndex]];
        const nextLayer = this.layers.baseLayers[layerNames[nextIndex]];
        
        this.map.removeLayer(currentLayer);
        nextLayer.addTo(this.map);
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    setupLegend() {
        const legend = L.control({ position: 'bottomleft' });
        
        legend.onAdd = () => {
            const div = L.DomUtil.create('div', 'legend');
            div.innerHTML = `
                <h4>Map Legend</h4>
                
                <h5>Assets</h5>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.assetStyles.water.fillColor}"></div>
                    <span>Water Bodies</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.assetStyles.forest.fillColor}"></div>
                    <span>Forest</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.assetStyles.agricultural.fillColor}"></div>
                    <span>Agricultural Land</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.assetStyles.homestead.fillColor}"></div>
                    <span>Homestead</span>
                </div>
                
                <h5>FRA Claims</h5>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.fraStyles.IFR.fillColor}; border-style: dashed;"></div>
                    <span>Individual Forest Rights</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.fraStyles.CFR.fillColor}; border-style: dashed;"></div>
                    <span>Community Forest Rights</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.fraStyles.CR.fillColor}; border-style: dashed;"></div>
                    <span>Community Resource Rights</span>
                </div>
                
                <h5>Administrative</h5>
                <div class="legend-item">
                    <div class="legend-color" style="border: 3px dashed ${this.adminStyles.state.color}; background: transparent;"></div>
                    <span>State Boundaries</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="border: 2px dashed ${this.adminStyles.district.color}; background: transparent;"></div>
                    <span>District Boundaries</span>
                </div>
            `;
            return div;
        };
        
        legend.addTo(this.map);
    }
    
    showLoading(show) {
        const loadingDiv = document.getElementById('loading');
        loadingDiv.style.display = show ? 'block' : 'none';
    }
    
    showError(message) {
        alert(`Error: ${message}`);
    }
    
    updateStatistics() {
        // Update asset count
        const totalAssets = this.data.assets ? this.data.assets.features.length : 0;
        const totalFRA = this.data.fra ? this.data.fra.features.length : 0;
        
        const totalAssetsEl = document.getElementById('total-assets');
        const totalFRAEl = document.getElementById('total-fra');
        
        if (totalAssetsEl) totalAssetsEl.textContent = totalAssets.toLocaleString();
        if (totalFRAEl) totalFRAEl.textContent = totalFRA.toLocaleString();
        
        console.log(`Statistics updated: ${totalAssets} assets, ${totalFRA} FRA claims`);
    }
    
    updateZoomStatistic() {
        const zoomEl = document.getElementById('map-zoom');
        if (zoomEl) {
            zoomEl.textContent = this.map.getZoom();
        }
    }
    
    setupOpacityControls() {
        // Setup opacity value display updates
        const opacityControls = [
            { slider: 'assets-opacity', display: 'assets-opacity-value' },
            { slider: 'fra-opacity', display: 'fra-opacity-value' },
            { slider: 'admin-opacity', display: 'admin-opacity-value' }
        ];
        
        opacityControls.forEach(control => {
            const slider = document.getElementById(control.slider);
            const display = document.getElementById(control.display);
            
            if (slider && display) {
                slider.addEventListener('input', (e) => {
                    const value = Math.round(e.target.value * 100);
                    display.textContent = `${value}%`;
                });
            }
        });
    }
}

// Initialize the WebGIS when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.indiaWebGIS = new IndiaWebGIS();
});