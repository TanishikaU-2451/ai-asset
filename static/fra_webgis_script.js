/**
 * FRA WebGIS Integration
 * Comprehensive Forest Rights Act (IFR/CFR/CR) management system
 */

class FRAWebGIS {
    constructor() {
        this.map = null;
        this.layers = {};
        this.currentFilters = {};
        this.analytics = {};
        this.performanceMetrics = {};
        
        // FRA type styles
        this.fraTypeStyles = {
            'IFR': { color: '#007bff', fillColor: '#007bff', fillOpacity: 0.7, weight: 2 },
            'CFR': { color: '#28a745', fillColor: '#28a745', fillOpacity: 0.7, weight: 2 },
            'CR': { color: '#ffc107', fillColor: '#ffc107', fillOpacity: 0.7, weight: 2 }
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
                <h4>FRA Claim Types</h4>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.fraTypeStyles.IFR.fillColor}"></div>
                    <span>Individual Forest Rights (IFR)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.fraTypeStyles.CFR.fillColor}"></div>
                    <span>Community Forest Rights (CFR)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background-color: ${this.fraTypeStyles.CR.fillColor}"></div>
                    <span>Community Resource Rights (CR)</span>
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
        
        // Analytics buttons
        document.getElementById('view-analytics').addEventListener('click', () => {
            this.showAnalytics();
        });
        
        document.getElementById('view-timeline').addEventListener('click', () => {
            this.showTimelineAnalysis();
        });
        
        document.getElementById('view-tribal').addEventListener('click', () => {
            this.showTribalAnalysis();
        });
        
        // Map actions
        document.getElementById('export-data').addEventListener('click', () => {
            this.exportData();
        });
        
        document.getElementById('fullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });
        
        document.getElementById('reset-view').addEventListener('click', () => {
            this.resetMapView();
        });
        
        // Layer controls
        document.getElementById('layer-ifr').addEventListener('change', (e) => {
            this.toggleLayer('IFR', e.target.checked);
        });
        
        document.getElementById('layer-cfr').addEventListener('change', (e) => {
            this.toggleLayer('CFR', e.target.checked);
        });
        
        document.getElementById('layer-cr').addEventListener('change', (e) => {
            this.toggleLayer('CR', e.target.checked);
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
            
            // Load performance metrics
            await this.loadPerformanceMetrics();
            
            // Load initial claims data
            await this.loadClaims();
            
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
    
    async loadPerformanceMetrics() {
        try {
            const response = await fetch('/api/performance');
            const metrics = await response.json();
            
            this.performanceMetrics = metrics;
            this.updateQuickStats(metrics);
            
        } catch (error) {
            console.error('Error loading performance metrics:', error);
        }
    }
    
    updateQuickStats(metrics) {
        document.getElementById('total-claims').textContent = metrics.total_claims || 0;
        document.getElementById('approved-claims').textContent = metrics.approved_claims || 0;
        document.getElementById('pending-claims').textContent = metrics.pending_claims || 0;
        document.getElementById('total-area').textContent = (metrics.total_area_ha || 0).toLocaleString();
    }
    
    async loadClaims() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`/api/claims?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Claims data received:', data);
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (!data.features || !Array.isArray(data.features)) {
                throw new Error('Invalid data format: missing features array');
            }
            
            this.processClaimsData(data);
            this.updateFeatureCount(data.features.length);
            
        } catch (error) {
            console.error('Error loading claims:', error);
            this.showError(`Failed to load claims data: ${error.message}`);
        }
    }
    
    processClaimsData(geojsonData) {
        console.log('Processing claims data:', geojsonData);
        
        // Clear existing layers
        Object.values(this.layers).forEach(layer => {
            if (layer && this.map.hasLayer(layer)) {
                this.map.removeLayer(layer);
            }
        });
        this.layers = {};
        
        // Group features by FRA type
        const featuresByType = {};
        
        geojsonData.features.forEach(feature => {
            const fraType = feature.properties.fra_type;
            if (!featuresByType[fraType]) {
                featuresByType[fraType] = [];
            }
            featuresByType[fraType].push(feature);
        });
        
        console.log('Features grouped by type:', featuresByType);
        
        // Create layers for each FRA type
        Object.entries(featuresByType).forEach(([fraType, features]) => {
            if (features.length > 0) {
                console.log(`Creating layer for ${fraType} with ${features.length} features`);
                
                this.layers[fraType] = L.geoJSON(features, {
                    style: this.fraTypeStyles[fraType] || this.fraTypeStyles.IFR,
                    onEachFeature: (feature, layer) => {
                        this.addClaimPopup(feature, layer);
                    }
                });
                
                // Add to map if layer is enabled
                const layerCheckbox = document.getElementById(`layer-${fraType.toLowerCase()}`);
                console.log(`Layer checkbox for ${fraType}:`, layerCheckbox, layerCheckbox?.checked);
                
                if (layerCheckbox && layerCheckbox.checked) {
                    this.map.addLayer(this.layers[fraType]);
                    console.log(`Added ${fraType} layer to map`);
                }
            }
        });
        
        console.log('Final layers:', this.layers);
    }
    
    addClaimPopup(feature, layer) {
        const props = feature.properties;
        let popupContent = `
            <div class="popup-title">
                <span class="fra-type-indicator ${props.fra_type}">${props.fra_type}</span>
                ${props.claim_id}
            </div>
        `;
        
        // Basic information
        popupContent += `<div class="popup-details">
            <span class="popup-label">Status:</span> 
            <span class="popup-value">
                <span class="status-indicator ${props.status}"></span>${props.status_name}
            </span>
        </div>`;
        
        if (props.state) popupContent += `<div class="popup-details"><span class="popup-label">State:</span> <span class="popup-value">${props.state}</span></div>`;
        if (props.district) popupContent += `<div class="popup-details"><span class="popup-label">District:</span> <span class="popup-value">${props.district}</span></div>`;
        if (props.village) popupContent += `<div class="popup-details"><span class="popup-label">Village:</span> <span class="popup-value">${props.village}</span></div>`;
        if (props.claim_area_ha) popupContent += `<div class="popup-details"><span class="popup-label">Area:</span> <span class="popup-value">${props.claim_area_ha} ha</span></div>`;
        
        // FRA specific information
        if (props.fra_type_name) popupContent += `<div class="popup-details"><span class="popup-label">Type:</span> <span class="popup-value">${props.fra_type_name}</span></div>`;
        if (props.tribal_community) popupContent += `<div class="popup-details"><span class="popup-label">Community:</span> <span class="popup-value">${props.tribal_community}</span></div>`;
        if (props.submission_date) popupContent += `<div class="popup-details"><span class="popup-label">Submitted:</span> <span class="popup-value">${props.submission_date}</span></div>`;
        
        // Add click handler for detailed view
        popupContent += `<div style="margin-top: 10px;">
            <button onclick="fraWebGIS.showClaimDetails('${props.claim_id}')" class="btn btn-small btn-primary">View Details</button>
        </div>`;
        
        layer.bindPopup(popupContent);
    }
    
    toggleLayer(fraType, visible) {
        const layer = this.layers[fraType];
        if (layer) {
            if (visible) {
                if (!this.map.hasLayer(layer)) {
                    this.map.addLayer(layer);
                }
            } else {
                if (this.map.hasLayer(layer)) {
                    this.map.removeLayer(layer);
                }
            }
        }
    }
    
    applyFilters() {
        // Collect filter values
        this.currentFilters = {
            state: document.getElementById('state-filter').value,
            district: document.getElementById('district-filter').value,
            village: document.getElementById('village-filter').value,
            fra_type: document.getElementById('fra-type-filter').value,
            status: document.getElementById('status-filter').value,
            tribal_community: document.getElementById('tribal-filter').value,
            claim_area_min: document.getElementById('area-min').value,
            claim_area_max: document.getElementById('area-max').value
        };
        
        // Remove empty filters
        this.currentFilters = Object.fromEntries(
            Object.entries(this.currentFilters).filter(([_, value]) => value)
        );
        
        // Reload claims with filters
        this.loadClaims();
    }
    
    clearFilters() {
        // Reset all filter inputs
        document.getElementById('state-filter').value = '';
        document.getElementById('district-filter').value = '';
        document.getElementById('village-filter').value = '';
        document.getElementById('fra-type-filter').value = '';
        document.getElementById('status-filter').value = '';
        document.getElementById('tribal-filter').value = '';
        document.getElementById('area-min').value = '';
        document.getElementById('area-max').value = '';
        
        // Clear current filters
        this.currentFilters = {};
        
        // Reload claims
        this.loadClaims();
    }
    
    async showAnalytics() {
        try {
            const response = await fetch('/api/analytics');
            const analytics = await response.json();
            
            this.analytics = analytics;
            this.displayAnalytics(analytics);
            
            document.getElementById('analytics-modal').style.display = 'block';
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics');
        }
    }
    
    displayAnalytics(analytics) {
        console.log('Analytics data:', analytics);
        
        // Create charts
        if (analytics.summary && analytics.summary.claims_by_type) {
            this.createFRATypeChart(analytics.summary.claims_by_type);
        }
        if (analytics.summary && analytics.summary.claims_by_status) {
            this.createStatusChart(analytics.summary.claims_by_status);
        }
        if (analytics.summary && analytics.summary.claims_by_state) {
            this.createStateChart(analytics.summary.claims_by_state);
        }
        if (analytics.timeline_analysis) {
            this.createTimelineChart(analytics.timeline_analysis);
        }
    }
    
    createFRATypeChart(data) {
        const ctx = document.getElementById('fra-type-chart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: ['#007bff', '#28a745', '#ffc107']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    createStatusChart(data) {
        const ctx = document.getElementById('status-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Claims',
                    data: Object.values(data),
                    backgroundColor: '#2c5530'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    createStateChart(data) {
        const ctx = document.getElementById('state-chart').getContext('2d');
        const sortedData = Object.entries(data)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10); // Top 10 states
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedData.map(([state]) => state),
                datasets: [{
                    label: 'Claims',
                    data: sortedData.map(([,count]) => count),
                    backgroundColor: '#17a2b8'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    createTimelineChart(data) {
        const ctx = document.getElementById('timeline-chart').getContext('2d');
        const years = Object.keys(data).sort();
        const claims = years.map(year => data[year].claims_submitted || 0);
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [{
                    label: 'Claims Submitted',
                    data: claims,
                    borderColor: '#2c5530',
                    backgroundColor: 'rgba(44, 85, 48, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    async showClaimDetails(claimId) {
        try {
            const response = await fetch(`/api/claim/${claimId}`);
            const claimDetails = await response.json();
            
            if (claimDetails.error) {
                throw new Error(claimDetails.error);
            }
            
            this.displayClaimDetails(claimDetails);
            document.getElementById('claim-modal').style.display = 'block';
            
        } catch (error) {
            console.error('Error loading claim details:', error);
            this.showError('Failed to load claim details');
        }
    }
    
    displayClaimDetails(claim) {
        const detailsContainer = document.getElementById('claim-details');
        
        let html = `
            <div class="claim-details">
                <div class="detail-section">
                    <h3>Basic Information</h3>
                    <div class="detail-item">
                        <span class="detail-label">Claim ID:</span>
                        <span class="detail-value">${claim.claim_id}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">FRA Type:</span>
                        <span class="detail-value">
                            <span class="fra-type-indicator ${claim.fra_type}">${claim.fra_type}</span>
                            ${claim.fra_type_name}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Status:</span>
                        <span class="detail-value">
                            <span class="status-indicator ${claim.status}"></span>
                            ${claim.status_name}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Area:</span>
                        <span class="detail-value">${claim.claim_area_ha} ha (${claim.claim_area_acres} acres)</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Location Details</h3>
                    <div class="detail-item">
                        <span class="detail-label">State:</span>
                        <span class="detail-value">${claim.state}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">District:</span>
                        <span class="detail-value">${claim.district}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Block:</span>
                        <span class="detail-value">${claim.block}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Village:</span>
                        <span class="detail-value">${claim.village}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3>Community Information</h3>
                    <div class="detail-item">
                        <span class="detail-label">Tribal Community:</span>
                        <span class="detail-value">${claim.tribal_community}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Applicant Type:</span>
                        <span class="detail-value">${claim.applicant_type}</span>
                    </div>
                    ${claim.applicant_name ? `
                    <div class="detail-item">
                        <span class="detail-label">Applicant Name:</span>
                        <span class="detail-value">${claim.applicant_name}</span>
                    </div>
                    ` : ''}
                    ${claim.community_name ? `
                    <div class="detail-item">
                        <span class="detail-label">Community Name:</span>
                        <span class="detail-value">${claim.community_name}</span>
                    </div>
                    ` : ''}
                </div>
                
                <div class="detail-section">
                    <h3>Timeline</h3>
                    <div class="detail-item">
                        <span class="detail-label">Submission Date:</span>
                        <span class="detail-value">${claim.submission_date}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Last Updated:</span>
                        <span class="detail-value">${claim.last_updated}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Field Verification:</span>
                        <span class="detail-value">${claim.field_verification_done ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">GPS Verified:</span>
                        <span class="detail-value">${claim.gps_coordinates_verified ? 'Yes' : 'No'}</span>
                    </div>
                </div>
            </div>
        `;
        
        detailsContainer.innerHTML = html;
    }
    
    async showTimelineAnalysis() {
        // Implementation for timeline analysis
        console.log('Timeline analysis requested');
    }
    
    async showTribalAnalysis() {
        // Implementation for tribal analysis
        console.log('Tribal analysis requested');
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
            a.download = `fra_claims_${new Date().toISOString().split('T')[0]}.json`;
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
    
    resetMapView() {
        this.map.setView([20.5937, 78.9629], 5);
    }
    
    updateFeatureCount(count) {
        const countElement = document.getElementById('feature-count');
        if (countElement) {
            countElement.textContent = `${count.toLocaleString()} claims`;
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
    
    showError(message) {
        console.error(message);
        // You could add a toast notification here
        alert(message);
    }
}

// Initialize the FRA WebGIS when the page loads
let fraWebGIS;
document.addEventListener('DOMContentLoaded', () => {
    fraWebGIS = new FRAWebGIS();
});
