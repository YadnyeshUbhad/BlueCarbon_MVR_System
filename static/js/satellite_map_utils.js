/**
 * Satellite Map Utilities for Blue Carbon MRV
 * Provides helper functions for map initialization, area drawing and coordinate management
 */

// Base map configuration with Indian coastal focus
const MAP_CONFIG = {
    defaultCenter: [15.2993, 78.5234], // Center of India
    defaultZoom: 5,
    minZoom: 4,
    maxZoom: 18,
    zoomControl: true,
    attribution: 'Map data &copy; OpenStreetMap contributors, Imagery © Mapbox/Esri'
};

// Indian coastal boundaries for validation
const COASTAL_BOUNDARIES = {
    west_coast: {
        states: ['Gujarat', 'Maharashtra', 'Goa', 'Karnataka', 'Kerala'],
        lat_range: [8.0, 24.0],
        lng_range: [68.0, 76.0]
    },
    east_coast: {
        states: ['West Bengal', 'Odisha', 'Andhra Pradesh', 'Tamil Nadu', 'Puducherry'],
        lat_range: [8.0, 22.5],
        lng_range: [77.0, 93.0]
    },
    islands: {
        regions: ['Lakshadweep', 'Andaman and Nicobar'],
        coordinates: [
            {name: 'Lakshadweep', lat: 10.5667, lng: 72.6417},
            {name: 'Andaman', lat: 11.7401, lng: 92.6586},
            {name: 'Nicobar', lat: 7.9403, lng: 93.9537}
        ]
    }
};

// Major coastal ecosystems for blue carbon
const ECOSYSTEM_TYPES = [
    {id: 'mangrove', name: 'Mangrove Forest'},
    {id: 'seagrass', name: 'Seagrass Meadow'},
    {id: 'salt_marsh', name: 'Salt Marsh'},
    {id: 'coastal_wetland', name: 'Coastal Wetland'},
    {id: 'mudflat', name: 'Mudflat'},
    {id: 'estuary', name: 'Estuary'}
];

/**
 * Initialize a Leaflet map with custom basemaps
 * @param {string} mapContainerId - HTML element ID for the map container
 * @param {Array} [initialCenter] - Optional initial center coordinates [lat, lng]
 * @param {number} [initialZoom] - Optional initial zoom level
 * @returns {L.Map} - The initialized Leaflet map object
 */
function initializeMap(mapContainerId, initialCenter, initialZoom) {
    // Use provided values or defaults
    const center = initialCenter || MAP_CONFIG.defaultCenter;
    const zoom = initialZoom || MAP_CONFIG.defaultZoom;
    
    // Create map instance
    const map = L.map(mapContainerId, {
        center: center,
        zoom: zoom,
        minZoom: MAP_CONFIG.minZoom,
        maxZoom: MAP_CONFIG.maxZoom,
        zoomControl: MAP_CONFIG.zoomControl
    });
    
    // Add basemap layers
    const basemaps = {
        "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }),
        "Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Imagery &copy; Esri'
        }),
        "Terrain": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap (CC-BY-SA)'
        }),
        "Hybrid": L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
            attribution: 'Map data &copy; Google'
        })
    };
    
    // Add the default basemap
    basemaps["Satellite"].addTo(map);
    
    // Add layer control
    L.control.layers(basemaps, {}, {collapsed: false}).addTo(map);
    
    // Add scale control
    L.control.scale({imperial: false}).addTo(map);
    
    // Add coordinates display control
    addCoordinatesControl(map);
    
    return map;
}

/**
 * Initialize Leaflet Draw controls for area selection
 * @param {L.Map} map - Leaflet map instance
 * @param {Function} onDrawCreated - Callback function when a shape is drawn
 * @returns {L.Control.Draw} - The draw control instance
 */
function initializeDrawControls(map, onDrawCreated) {
    // Create feature group to store drawn items
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    
    // Configure draw controls
    const drawControl = new L.Control.Draw({
        position: 'topright',
        draw: {
            polyline: false,
            circle: false,
            circlemarker: false,
            marker: {
                icon: new L.Icon.Default()
            },
            polygon: {
                allowIntersection: false,
                drawError: {
                    color: '#e1e100',
                    message: '<strong>Warning!</strong> Shape cannot intersect itself'
                },
                shapeOptions: {
                    color: '#3388ff'
                }
            },
            rectangle: {
                shapeOptions: {
                    color: '#3388ff'
                }
            }
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    
    map.addControl(drawControl);
    
    // Handle draw created event
    map.on(L.Draw.Event.CREATED, function(e) {
        drawnItems.addLayer(e.layer);
        if (typeof onDrawCreated === 'function') {
            onDrawCreated(e.layer);
        }
    });
    
    // Handle draw edited event
    map.on(L.Draw.Event.EDITED, function(e) {
        const layers = e.layers;
        layers.eachLayer(function(layer) {
            if (typeof onDrawCreated === 'function') {
                onDrawCreated(layer);
            }
        });
    });
    
    return {
        control: drawControl,
        featureGroup: drawnItems
    };
}

/**
 * Add mouse coordinate display to map
 * @param {L.Map} map - Leaflet map instance
 */
function addCoordinatesControl(map) {
    const coordinatesControl = L.control({position: 'bottomleft'});
    
    coordinatesControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'info coordinates-info');
        div.innerHTML = 'Coordinates: ';
        return div;
    };
    
    coordinatesControl.addTo(map);
    
    map.on('mousemove', function(e) {
        const coordDiv = document.querySelector('.coordinates-info');
        if (coordDiv) {
            coordDiv.innerHTML = `Lat: ${e.latlng.lat.toFixed(5)} | Lng: ${e.latlng.lng.toFixed(5)}`;
        }
    });
    
    return coordinatesControl;
}

/**
 * Add a search control to the map
 * @param {L.Map} map - Leaflet map instance
 */
function addSearchControl(map) {
    const searchControl = L.control({position: 'topleft'});
    
    searchControl.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'info search-control');
        div.innerHTML = `
            <div class="input-group">
                <input type="text" id="search-input" class="form-control" placeholder="Search location">
                <div class="input-group-append">
                    <button class="btn btn-outline-secondary" id="search-button" type="button">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
        `;
        return div;
    };
    
    searchControl.addTo(map);
    
    // Add search functionality
    setTimeout(() => {
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        
        if (searchInput && searchButton) {
            searchButton.addEventListener('click', function() {
                searchLocation(searchInput.value, map);
            });
            
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchLocation(searchInput.value, map);
                }
            });
        }
    }, 100);
    
    return searchControl;
}

/**
 * Search for a location by name or coordinates
 * @param {string} query - Location name or coordinates
 * @param {L.Map} map - Leaflet map instance
 */
function searchLocation(query, map) {
    if (!query.trim()) return;
    
    // Check if input is coordinates
    const coordsRegex = /^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/;
    
    if (coordsRegex.test(query)) {
        // Parse coordinates
        const parts = query.split(',');
        const lat = parseFloat(parts[0].trim());
        const lng = parseFloat(parts[1].trim());
        
        // Validate coordinates
        if (!isNaN(lat) && !isNaN(lng)) {
            map.setView([lat, lng], 12);
            L.marker([lat, lng]).addTo(map)
                .bindPopup(`Coordinates: ${lat.toFixed(5)}, ${lng.toFixed(5)}`)
                .openPopup();
            return;
        }
    }
    
    // Otherwise, search by name using Nominatim
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=in&limit=1`)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lon = parseFloat(result.lon);
                
                map.setView([lat, lon], 12);
                L.marker([lat, lon]).addTo(map)
                    .bindPopup(result.display_name)
                    .openPopup();
            } else {
                alert('Location not found. Please try a different search term.');
            }
        })
        .catch(error => {
            console.error('Error searching for location:', error);
            alert('Error searching for location. Please try again.');
        });
}

/**
 * Get user's current location and center map on it
 * @param {L.Map} map - Leaflet map instance
 */
function getUserLocation(map) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // Success callback
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                map.setView([lat, lng], 13);
                
                // Add a marker at user location
                const marker = L.marker([lat, lng]).addTo(map);
                marker.bindPopup('Your current location').openPopup();
            },
            // Error callback
            function(error) {
                let errorMessage;
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = "Location access denied. Please enable location services.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = "Location information unavailable.";
                        break;
                    case error.TIMEOUT:
                        errorMessage = "Location request timed out.";
                        break;
                    default:
                        errorMessage = "An unknown error occurred.";
                }
                alert(errorMessage);
            },
            // Options
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

/**
 * Add location button to map
 * @param {L.Map} map - Leaflet map instance
 */
function addLocationButton(map) {
    const locationButton = L.control({position: 'topleft'});
    
    locationButton.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'info location-button');
        div.innerHTML = `
            <button id="get-location-btn" class="btn btn-primary" title="Get your current location">
                <i class="fas fa-map-marker-alt"></i>
            </button>
        `;
        return div;
    };
    
    locationButton.addTo(map);
    
    setTimeout(() => {
        const button = document.getElementById('get-location-btn');
        if (button) {
            button.addEventListener('click', function() {
                getUserLocation(map);
            });
        }
    }, 100);
    
    return locationButton;
}

/**
 * Calculate area in hectares from a polygon
 * @param {L.Polygon|L.Rectangle} layer - Leaflet polygon or rectangle layer
 * @returns {number} - Area in hectares
 */
function calculateAreaInHectares(layer) {
    try {
        // Get the area in square meters
        let areaSqMeters;
        
        // Handle both polygons and rectangles
        if (layer instanceof L.Rectangle) {
            const bounds = layer.getBounds();
            const latlngs = [
                bounds.getNorthWest(),
                bounds.getNorthEast(),
                bounds.getSouthEast(),
                bounds.getSouthWest()
            ];
            // Create a temporary polygon to calculate area
            const polygon = L.polygon(latlngs);
            areaSqMeters = L.GeometryUtil.geodesicArea(polygon.getLatLngs()[0]);
        } else {
            areaSqMeters = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
        }
        
        // Convert to hectares (1 hectare = 10,000 sq meters)
        const areaHectares = areaSqMeters / 10000;
        
        return areaHectares;
    } catch (e) {
        console.error("Error calculating area:", e);
        return 0;
    }
}

/**
 * Get the center point of a polygon or rectangle
 * @param {L.Polygon|L.Rectangle} layer - Leaflet polygon or rectangle layer
 * @returns {L.LatLng} - Center point
 */
function getLayerCenter(layer) {
    if (layer instanceof L.Rectangle) {
        return layer.getBounds().getCenter();
    } else {
        return layer.getBounds().getCenter();
    }
}

/**
 * Get polygon coordinates as an array
 * @param {L.Polygon|L.Rectangle} layer - Leaflet polygon or rectangle layer
 * @returns {Array} - Array of [lat, lng] coordinates
 */
function getPolygonCoordinates(layer) {
    let coordinates = [];
    
    if (layer instanceof L.Rectangle) {
        const bounds = layer.getBounds();
        coordinates = [
            [bounds.getNorthWest().lat, bounds.getNorthWest().lng],
            [bounds.getNorthEast().lat, bounds.getNorthEast().lng],
            [bounds.getSouthEast().lat, bounds.getSouthEast().lng],
            [bounds.getSouthWest().lat, bounds.getSouthWest().lng]
        ];
    } else {
        const latLngs = layer.getLatLngs()[0];
        for (let i = 0; i < latLngs.length; i++) {
            coordinates.push([latLngs[i].lat, latLngs[i].lng]);
        }
    }
    
    return coordinates;
}

/**
 * Check if coordinates are in coastal region
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 * @returns {Object} - Result with validation information
 */
function validateCoastalLocation(lat, lng) {
    const result = {
        isCoastal: false,
        region: null,
        message: ""
    };
    
    // Check west coast
    if (COASTAL_BOUNDARIES.west_coast.lat_range[0] <= lat && 
        lat <= COASTAL_BOUNDARIES.west_coast.lat_range[1] &&
        COASTAL_BOUNDARIES.west_coast.lng_range[0] <= lng && 
        lng <= COASTAL_BOUNDARIES.west_coast.lng_range[1]) {
        
        result.isCoastal = true;
        result.region = "West Coast";
        result.message = "Location is on India's west coast.";
        return result;
    }
    
    // Check east coast
    if (COASTAL_BOUNDARIES.east_coast.lat_range[0] <= lat && 
        lat <= COASTAL_BOUNDARIES.east_coast.lat_range[1] &&
        COASTAL_BOUNDARIES.east_coast.lng_range[0] <= lng && 
        lng <= COASTAL_BOUNDARIES.east_coast.lng_range[1]) {
        
        result.isCoastal = true;
        result.region = "East Coast";
        result.message = "Location is on India's east coast.";
        return result;
    }
    
    // Check islands
    for (const island of COASTAL_BOUNDARIES.islands.coordinates) {
        // Simple distance check (very approximate)
        const distance = Math.sqrt(
            Math.pow(lat - island.lat, 2) + 
            Math.pow(lng - island.lng, 2)
        );
        
        if (distance < 3) { // Roughly 300km in degrees
            result.isCoastal = true;
            result.region = island.name;
            result.message = `Location is near ${island.name}.`;
            return result;
        }
    }
    
    result.message = "Location is not in a coastal region.";
    return result;
}

/**
 * Create a marker for a blue carbon project
 * @param {L.Map} map - Leaflet map instance
 * @param {Object} project - Project data object
 * @returns {L.Marker} - Marker instance
 */
function createProjectMarker(map, project) {
    // Create custom icon based on ecosystem type
    let iconUrl = '/static/images/markers/default-marker.png';
    
    switch(project.ecosystem_type) {
        case 'mangrove':
            iconUrl = '/static/images/markers/mangrove-marker.png';
            break;
        case 'seagrass':
            iconUrl = '/static/images/markers/seagrass-marker.png';
            break;
        case 'salt_marsh':
            iconUrl = '/static/images/markers/saltmarsh-marker.png';
            break;
        default:
            iconUrl = '/static/images/markers/default-marker.png';
    }
    
    // Fallback to default marker if custom icon fails to load
    const customIcon = L.icon({
        iconUrl: iconUrl,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });
    
    const marker = L.marker([project.latitude, project.longitude], {
        icon: customIcon,
        title: project.name
    }).addTo(map);
    
    // Create popup content
    const popupContent = `
        <div class="project-popup">
            <h5>${project.name}</h5>
            <p><strong>Type:</strong> ${project.ecosystem_type}</p>
            <p><strong>Area:</strong> ${project.area} ha</p>
            <p><strong>Status:</strong> ${project.status}</p>
            ${project.description ? `<p>${project.description}</p>` : ''}
            <button class="btn btn-sm btn-primary view-project-btn" 
                    data-project-id="${project.id}">View Details</button>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    
    // Add click handler for view details button
    marker.on('popupopen', function() {
        setTimeout(() => {
            const viewBtn = document.querySelector(`.view-project-btn[data-project-id="${project.id}"]`);
            if (viewBtn) {
                viewBtn.addEventListener('click', function() {
                    // Navigate to project detail page
                    window.location.href = `/projects/${project.id}`;
                });
            }
        }, 100);
    });
    
    return marker;
}

/**
 * Draw a polygon for a project area
 * @param {L.Map} map - Leaflet map instance
 * @param {Array} coordinates - Array of [lat, lng] coordinates
 * @param {Object} project - Project data
 * @returns {L.Polygon} - Polygon instance
 */
function drawProjectArea(map, coordinates, project) {
    // Style based on ecosystem type
    let fillColor = '#3388ff';
    let fillOpacity = 0.2;
    
    switch(project.ecosystem_type) {
        case 'mangrove':
            fillColor = '#006400'; // Dark green
            break;
        case 'seagrass':
            fillColor = '#66CDAA'; // Medium aquamarine
            break;
        case 'salt_marsh':
            fillColor = '#8B8970'; // Light yellow brown
            break;
        case 'coastal_wetland':
            fillColor = '#6B8E23'; // Olive drab
            break;
        default:
            fillColor = '#3388ff'; // Default blue
    }
    
    const polygon = L.polygon(coordinates, {
        color: fillColor,
        weight: 3,
        opacity: 0.7,
        fillColor: fillColor,
        fillOpacity: fillOpacity,
        className: `project-area-${project.id}`
    }).addTo(map);
    
    // Add project data to polygon
    polygon.project = project;
    
    // Add popup with project info
    const popupContent = `
        <div class="project-area-popup">
            <h5>${project.name}</h5>
            <p><strong>Ecosystem:</strong> ${project.ecosystem_type}</p>
            <p><strong>Area:</strong> ${project.area.toFixed(2)} ha</p>
            <button class="btn btn-sm btn-info zoom-to-area-btn">Zoom to Area</button>
            <button class="btn btn-sm btn-primary view-details-btn" 
                    data-project-id="${project.id}">View Details</button>
        </div>
    `;
    
    polygon.bindPopup(popupContent);
    
    // Add click handlers for popup buttons
    polygon.on('popupopen', function() {
        setTimeout(() => {
            const zoomBtn = document.querySelector('.zoom-to-area-btn');
            const viewBtn = document.querySelector(`.view-details-btn[data-project-id="${project.id}"]`);
            
            if (zoomBtn) {
                zoomBtn.addEventListener('click', function() {
                    map.fitBounds(polygon.getBounds());
                });
            }
            
            if (viewBtn) {
                viewBtn.addEventListener('click', function() {
                    // Navigate to project detail page
                    window.location.href = `/projects/${project.id}`;
                });
            }
        }, 100);
    });
    
    return polygon;
}

// Export all functions
window.SatelliteMapUtils = {
    initializeMap,
    initializeDrawControls,
    addCoordinatesControl,
    addSearchControl,
    addLocationButton,
    searchLocation,
    getUserLocation,
    calculateAreaInHectares,
    getLayerCenter,
    getPolygonCoordinates,
    validateCoastalLocation,
    createProjectMarker,
    drawProjectArea,
    COASTAL_BOUNDARIES,
    ECOSYSTEM_TYPES,
    MAP_CONFIG
};