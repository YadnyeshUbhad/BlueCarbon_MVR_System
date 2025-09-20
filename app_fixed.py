from flask import Flask, request, Response, render_template, redirect, url_for, jsonify, session, flash
from flask import Blueprint
import os
import json
import csv
import io
import base64
from PIL import Image, ExifTags
import exifread
import numpy as np
import cv2
from datetime import datetime, timedelta
import random
import qrcode
import pyotp
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Create uploads directory if it doesn't exist
UPLOADS_FOLDER = 'uploads'
if not os.path.exists(UPLOADS_FOLDER):
    os.makedirs(UPLOADS_FOLDER)

# In-memory data storage (in production, use a proper database)
user_profiles = {}
credits_data = []
transactions_data = []
user_2fa_secrets = {}

# Utility functions for image analysis
def extract_gps_info(image_path):
    """Extract GPS coordinates from image EXIF data"""
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            
        lat = None
        lon = None
        
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            # Convert GPS coordinates
            lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))
            lat_deg = tags['GPS GPSLatitude']
            lat = float(lat_deg.values[0]) + float(lat_deg.values[1])/60 + float(lat_deg.values[2])/3600
            if lat_ref == 'S':
                lat = -lat
                
            lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))
            lon_deg = tags['GPS GPSLongitude']
            lon = float(lon_deg.values[0]) + float(lon_deg.values[1])/60 + float(lon_deg.values[2])/3600
            if lon_ref == 'W':
                lon = -lon
                
        return lat, lon
    except Exception as e:
        print(f"Error extracting GPS: {e}")
        return None, None

def detect_tree_in_image(image_path):
    """Detect if image contains trees using advanced computer vision"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Invalid image file"
        
        # Convert to HSV for better vegetation detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define ranges for vegetation (green and brown for trunks)
        green_lower = np.array([35, 50, 50])
        green_upper = np.array([85, 255, 255])
        brown_lower = np.array([8, 50, 20])
        brown_upper = np.array([20, 255, 200])
        
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        brown_mask = cv2.inRange(hsv, brown_lower, brown_upper)
        
        # Calculate vegetation percentage
        green_percentage = (cv2.countNonZero(green_mask) / (img.shape[0] * img.shape[1])) * 100
        brown_percentage = (cv2.countNonZero(brown_mask) / (img.shape[0] * img.shape[1])) * 100
        
        # Tree detection criteria: sufficient green (leaves) and some brown (trunk)
        is_tree = green_percentage > 20 and brown_percentage > 2
        
        # Additional check using edge detection for tree structure
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for vertical structures (tree trunks)
        vertical_structures = 0
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Minimum size
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = h / w if w > 0 else 0
                if aspect_ratio > 1.5:  # Tall structures
                    vertical_structures += 1
        
        # Enhanced tree detection
        is_tree = is_tree and (vertical_structures > 0 or green_percentage > 30)
        
        return is_tree, None
        
    except Exception as e:
        return False, f"Error analyzing image: {str(e)}"

def estimate_tree_dimensions_from_image(image_path):
    """Estimate tree dimensions from image analysis"""
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Find contours to estimate tree dimensions
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find the largest contour (assumed to be the main tree)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Estimate dimensions (these are rough estimates for demo)
        # In production, use calibrated measurements or reference objects
        estimated_height = random.uniform(5, 25)  # meters
        estimated_dbh = random.uniform(0.1, 1.2)  # meters
        
        return {
            'height': estimated_height,
            'dbh': estimated_dbh,
            'crown_width': w / h * estimated_height * 0.7  # rough crown width estimate
        }
        
    except Exception as e:
        print(f"Error estimating dimensions: {e}")
        return None

def calculate_tree_carbon_sequestration(height, dbh, latitude, longitude, species=None, age=None):
    """Calculate accurate carbon sequestration for individual trees using scientific formulas"""
    
    try:
        # Convert inputs to float
        height = float(height)
        dbh = float(dbh)
        latitude = float(latitude)
        longitude = float(longitude)
        age = float(age) if age else None
        
        # Species-specific parameters (Wood Density in kg/m³)
        species_params = {
            'Rhizophora': {'wood_density': 800, 'growth_rate': 1.2, 'allometric_a': 0.251, 'allometric_b': 2.46},  # Mangrove
            'Avicennia': {'wood_density': 650, 'growth_rate': 1.0, 'allometric_a': 0.251, 'allometric_b': 2.46},
            'Casuarina': {'wood_density': 600, 'growth_rate': 1.5, 'allometric_a': 0.25, 'allometric_b': 2.4},
            'Coconut Palm': {'wood_density': 400, 'growth_rate': 0.8, 'allometric_a': 0.22, 'allometric_b': 2.3},
            'Neem': {'wood_density': 680, 'growth_rate': 1.1, 'allometric_a': 0.26, 'allometric_b': 2.5},
            'Banyan': {'wood_density': 550, 'growth_rate': 2.0, 'allometric_a': 0.28, 'allometric_b': 2.6},
            'Teak': {'wood_density': 650, 'growth_rate': 1.3, 'allometric_a': 0.24, 'allometric_b': 2.4},
            'Eucalyptus': {'wood_density': 500, 'growth_rate': 2.5, 'allometric_a': 0.21, 'allometric_b': 2.3}
        }
        
        # Default parameters if species not specified
        default_params = {'wood_density': 600, 'growth_rate': 1.2, 'allometric_a': 0.25, 'allometric_b': 2.4}
        params = species_params.get(species, default_params)
        
        # Calculate biomass using allometric equations
        # Formula: AGB = a × DBH^b (where AGB = Above Ground Biomass in kg)
        dbh_cm = dbh * 100  # Convert to cm
        
        if dbh_cm > 5:  # Only for trees with DBH > 5cm
            # Chave et al. (2014) tropical forest equation
            # AGB = 0.0673 × (ρ × DBH² × H)^0.976
            # Where ρ = wood density, DBH in cm, H in m
            
            wood_density = params['wood_density'] / 1000  # Convert to g/cm³
            agb = 0.0673 * ((wood_density * (dbh_cm ** 2) * height) ** 0.976)
            
        else:
            # For smaller trees, use simpler allometric equation
            agb = params['allometric_a'] * (dbh_cm ** params['allometric_b'])
        
        # Calculate Below Ground Biomass (typically 15-30% of AGB)
        bgb = agb * 0.2
        
        # Total biomass
        total_biomass = agb + bgb
        
        # Convert biomass to carbon content (typically 47% of dry biomass)
        carbon_content = total_biomass * 0.47
        
        # Convert carbon to CO2 equivalent (CO2 = C × 44/12)
        co2_sequestered = carbon_content * (44/12)
        
        # Climate zone adjustment based on latitude
        if abs(latitude) < 23.5:  # Tropical
            climate_factor = 1.2
        elif abs(latitude) < 40:  # Subtropical
            climate_factor = 1.0
        else:  # Temperate
            climate_factor = 0.8
        
        co2_sequestered *= climate_factor
        
        # Annual sequestration rate (trees continue growing)
        if age:
            # Younger trees sequester more CO2 per year
            age_factor = max(0.5, 2 - (age / 50))  # Decreases with age
        else:
            age_factor = 1.0
        
        annual_sequestration = co2_sequestered * params['growth_rate'] * age_factor / 100
        
        # Convert kg to tonnes
        total_co2_tonnes = co2_sequestered / 1000
        annual_co2_tonnes = annual_sequestration / 1000
        
        return {
            'total_biomass_kg': round(total_biomass, 2),
            'carbon_content_kg': round(carbon_content, 2),
            'total_co2_sequestered_tonnes': round(total_co2_tonnes, 3),
            'annual_co2_sequestration_tonnes': round(annual_co2_tonnes, 3),
            'above_ground_biomass_kg': round(agb, 2),
            'below_ground_biomass_kg': round(bgb, 2),
            'wood_density': params['wood_density'],
            'climate_factor': climate_factor
        }
        
    except (ValueError, ZeroDivisionError, TypeError) as e:
        return None

def predict_species_and_carbon(image_path, manual_data=None):
    """Enhanced tree analysis with accurate carbon calculations"""
    try:
        # First, check if image contains trees
        is_tree, error = detect_tree_in_image(image_path)
        
        if error:
            return None, None, None, error
            
        if not is_tree:
            return None, None, None, "Invalid: Image does not contain trees. Only tree images are supported for accurate carbon calculations."
        
        # If manual data is provided, use it; otherwise estimate from image
        if manual_data:
            height = manual_data.get('height')
            dbh = manual_data.get('dbh')
            latitude = manual_data.get('latitude')
            longitude = manual_data.get('longitude')
            species = manual_data.get('species')
            age = manual_data.get('age')
        else:
            # Estimate dimensions from image
            dimensions = estimate_tree_dimensions_from_image(image_path)
            if not dimensions:
                return None, None, None, "Could not estimate tree dimensions from image"
            
            height = dimensions['height']
            dbh = dimensions['dbh']
            latitude = random.uniform(8, 35)  # Default to Indian latitude range
            longitude = random.uniform(68, 97)  # Default to Indian longitude range
            species = random.choice(['Neem', 'Banyan', 'Teak', 'Casuarina', 'Coconut Palm'])
            age = None
        
        # Calculate accurate carbon sequestration
        carbon_calc = calculate_tree_carbon_sequestration(
            height, dbh, latitude, longitude, species, age
        )
        
        if not carbon_calc:
            return None, None, None, "Error calculating carbon sequestration"
        
        # Return results in expected format
        carbon_rate = carbon_calc['annual_co2_sequestration_tonnes']
        carbon_credits = carbon_calc['total_co2_sequestered_tonnes']
        
        return species, carbon_rate, carbon_credits, None
        
    except Exception as e:
        return None, None, None, f"Error processing image: {str(e)}"

def generate_dummy_credits():
    """Generate dummy credit data for demonstration"""
    if not credits_data:
        projects = ['Mangrove Restoration Chennai', 'Seagrass Conservation Kerala', 'Coastal Forest Tamil Nadu']
        for i in range(15):
            credits_data.append({
                'id': i+1,
                'project': random.choice(projects),
                'vintage': random.randint(2020, 2024),
                'amount': random.randint(50, 500),
                'verification': random.choice(['Verified', 'Pending', 'Under Review']),
                'token': f"BC{random.randint(100000, 999999)}",
                'status': random.choice(['Available', 'Sold', 'Reserved']),
                'revenue': random.randint(10000, 100000),
                'date_created': datetime.now() - timedelta(days=random.randint(1, 365))
            })

def generate_dummy_transactions():
    """Generate dummy transaction data"""
    if not transactions_data:
        projects = ['Mangrove Restoration Chennai', 'Seagrass Conservation Kerala']
        buyers = ['EcoTech Corp', 'Green Industries Ltd', 'Carbon Offset Solutions']
        for i in range(10):
            credits = random.randint(10, 100)
            price = random.randint(150, 300)
            transactions_data.append({
                'id': f"TXN{random.randint(100000, 999999)}",
                'project': random.choice(projects),
                'credits': credits,
                'price': price,
                'total': credits * price,
                'buyer': random.choice(buyers),
                'date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'status': random.choice(['Completed', 'Pending', 'Processing'])
            })

@app.route("/")
def dashboard():
    return render_template("index.html")

# NGO blueprint for dashboard sections
ngo_bp = Blueprint("ngo", __name__, url_prefix="/ngo")

@ngo_bp.route("/")
def ngo_home():
    return redirect(url_for("ngo.dashboard_view"))

@ngo_bp.route("/dashboard")
def dashboard_view():
    # Enhanced stats with sample data
    stats = {
        "total_projects": 12,
        "approved_projects": 8,
        "credits_earned": 2450,
        "pending_verifications": 3,
        "reversed_applications": 1,
        "revenue_generated": 485000,
        "projects_change": 15,
        "approved_change": 87,
        "credits_change": 32,
        "reversed_change": 75,
        "revenue_change": 28,
        "avg_verification_time": 14,
    }
    
    recent_activities = [
        {
            "title": "Mangrove Restoration Project approved by NCCR",
            "time": "2 hours ago",
            "type": "success"
        },
        {
            "title": "New project verification started",
            "time": "5 hours ago",
            "type": "primary"
        },
        {
            "title": "Credits payment of ₹85,000 received",
            "time": "1 day ago",
            "type": "success"
        },
        {
            "title": "Seagrass restoration documentation uploaded",
            "time": "2 days ago",
            "type": "primary"
        },
        {
            "title": "Monthly compliance report submitted",
            "time": "3 days ago",
            "type": "primary"
        }
    ]
    
    return render_template("ngo/dashboard.html", stats=stats, recent_activities=recent_activities)

@ngo_bp.route("/profile", methods=["GET", "POST"])
def profile_view():
    if request.method == "POST":
        # Handle form submission
        profile_data = {
            "name": request.form.get("name"),
            "type": request.form.get("type"),
            "registration_number": request.form.get("registration_number"),
            "contact_person": request.form.get("contact_person"),
            "contact_phone": request.form.get("contact_phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address"),
            "district": request.form.get("district"),
            "state": request.form.get("state"),
            "payment_method": request.form.get("payment_method"),
            "bank_name": request.form.get("bank_name"),
            "account_number": request.form.get("account_number"),
            "ifsc_code": request.form.get("ifsc_code"),
            "account_holder_name": request.form.get("account_holder_name"),
            "wallet_address": request.form.get("wallet_address"),
            "wallet_type": request.form.get("wallet_type"),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store in memory (use database in production)
        user_profiles['default_user'] = profile_data
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('ngo.profile_view'))
    
    # GET request - show profile
    profile = user_profiles.get('default_user', {
        "name": "Green Coastal Initiative",
        "type": "ngo",
        "registration_number": "NGO/REG/2020/001245",
        "contact_person": "Dr. Priya Sharma",
        "contact_phone": "+91-9876543210",
        "email": "contact@greencoastal.org",
        "address": "123 Marine Drive, Coastal Conservation Center\nMumbai, Maharashtra 400001",
        "district": "Mumbai",
        "state": "Maharashtra",
        "join_date": "2020",
        "total_projects": 12,
        "total_credits": 2450,
        "total_revenue": 485000,
        "payment_method": "both",
        "bank_name": "State Bank of India",
        "account_number": "**********3456",
        "ifsc_code": "SBIN0001234",
        "account_holder_name": "Green Coastal Initiative",
        "wallet_address": "0x742d35Cc6634C0532925a3b8D93e0F93239D6789",
        "wallet_type": "metamask",
        "two_factor_enabled": False
    })
    return render_template("ngo/profile.html", profile=profile)

# Two-Factor Authentication Routes
@ngo_bp.route("/2fa/setup", methods=["GET", "POST"])
def setup_2fa():
    if request.method == "POST":
        # Generate secret key
        secret = pyotp.random_base32()
        user_2fa_secrets['default_user'] = secret
        
        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name="Green Coastal Initiative",
            issuer_name="BlueCarbon Platform"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'secret': secret,
            'qr_code': f'data:image/png;base64,{qr_code}'
        })
    
    return jsonify({'error': 'Method not allowed'})

@ngo_bp.route("/2fa/enable", methods=["POST"])
def enable_2fa():
    code = request.json.get('code')
    secret = user_2fa_secrets.get('default_user')
    
    if not secret:
        return jsonify({'success': False, 'message': 'No 2FA setup found'})
    
    totp = pyotp.TOTP(secret)
    if totp.verify(code):
        # Update profile to enable 2FA
        if 'default_user' in user_profiles:
            user_profiles['default_user']['two_factor_enabled'] = True
        return jsonify({'success': True, 'message': '2FA enabled successfully'})
    else:
        return jsonify({'success': False, 'message': 'Invalid verification code'})

@ngo_bp.route("/projects")
def projects_list():
    projects = []
    return render_template("ngo/projects.html", projects=projects)

@ngo_bp.route("/projects/new", methods=["GET", "POST"])
def project_new():
    if request.method == "POST":
        try:
            # Handle file uploads
            uploaded_files = request.files.getlist('media')
            project_data = {
                'name': request.form.get('name'),
                'ecosystem': request.form.get('ecosystem'),
                'description': request.form.get('description'),
                'start_date': request.form.get('start_date'),
                'area': request.form.get('area'),
                'admin_area': request.form.get('admin_area'),
                'species': request.form.get('species'),
                'seedlings': request.form.get('seedlings'),
                'created_at': datetime.now(),
                'images': []
            }
            
            total_carbon_credits = 0
            detected_species = []
            locations = []
            
            for file in uploaded_files:
                if file and file.filename:
                    # Save uploaded file
                    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
                    filepath = os.path.join(UPLOADS_FOLDER, filename)
                    file.save(filepath)
                    
                    # Extract GPS coordinates
                    lat, lon = extract_gps_info(filepath)
                    
                    # Predict species and carbon absorption
                    species, carbon_rate, carbon_credits, error = predict_species_and_carbon(filepath)
                    
                    image_info = {
                        'filename': filename,
                        'filepath': filepath,
                        'species': species,
                        'carbon_rate': carbon_rate,
                        'carbon_credits': carbon_credits,
                        'latitude': lat,
                        'longitude': lon,
                        'error': error
                    }
                    
                    project_data['images'].append(image_info)
                    
                    if species:
                        detected_species.append(species)
                        total_carbon_credits += carbon_credits or 0
                    
                    if lat and lon:
                        locations.append({'lat': lat, 'lon': lon})
            
            # Auto-populate fields based on AI analysis
            if detected_species:
                project_data['detected_species'] = list(set(detected_species))
                project_data['estimated_carbon_credits'] = total_carbon_credits
                project_data['average_location'] = {
                    'lat': sum(loc['lat'] for loc in locations) / len(locations) if locations else None,
                    'lon': sum(loc['lon'] for loc in locations) / len(locations) if locations else None
                }
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'project_data': project_data,
                    'auto_filled': {
                        'species': detected_species,
                        'carbon_credits': total_carbon_credits,
                        'location': project_data.get('average_location')
                    }
                })
            
            flash('Project registered successfully with AI-powered analysis!', 'success')
            return redirect(url_for('ngo.projects_list'))
            
        except Exception as e:
            error_msg = f"Error processing project: {str(e)}"
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg})
            flash(error_msg, 'error')
    
    return render_template("ngo/project_new.html")

@ngo_bp.route("/upload/analyze", methods=["POST"])
def analyze_uploaded_image():
    """API endpoint for real-time image analysis"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No image selected'})
    
    try:
        # Save temporary file
        filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(UPLOADS_FOLDER, filename)
        file.save(filepath)
        
        # Extract GPS and analyze image
        lat, lon = extract_gps_info(filepath)
        
        # Get manual measurements if provided
        manual_data = None
        if request.form:
            manual_data = {
                'height': request.form.get('height'),
                'dbh': request.form.get('dbh'),
                'latitude': request.form.get('latitude') or lat,
                'longitude': request.form.get('longitude') or lon,
                'species': request.form.get('species'),
                'age': request.form.get('age')
            }
            # Filter out None values
            manual_data = {k: v for k, v in manual_data.items() if v is not None and v != ''}
        
        species, carbon_rate, carbon_credits, error = predict_species_and_carbon(filepath, manual_data)
        
        # Clean up temp file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if error:
            return jsonify({'success': False, 'error': error})
        
        return jsonify({
            'success': True,
            'analysis': {
                'species': species,
                'carbon_absorption_rate': round(carbon_rate, 3),
                'estimated_carbon_credits': round(carbon_credits, 3),
                'location': {
                    'latitude': lat,
                    'longitude': lon
                } if lat and lon else None,
                'calculation_method': 'scientific_allometric' if manual_data else 'image_estimation'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@ngo_bp.route("/calculate/tree_carbon", methods=["POST"])
def calculate_tree_carbon():
    """API endpoint for calculating tree carbon sequestration using measurements"""
    try:
        data = request.get_json()
        
        # Required parameters
        height = data.get('height')
        dbh = data.get('dbh')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Optional parameters
        species = data.get('species')
        age = data.get('age')
        
        # Validate required parameters
        if not all([height, dbh, latitude, longitude]):
            return jsonify({
                'success': False, 
                'error': 'Missing required parameters: height, dbh, latitude, longitude'
            })
        
        # Calculate carbon sequestration
        result = calculate_tree_carbon_sequestration(
            height, dbh, latitude, longitude, species, age
        )
        
        if not result:
            return jsonify({
                'success': False, 
                'error': 'Error calculating carbon sequestration with provided parameters'
            })
        
        return jsonify({
            'success': True,
            'calculation': {
                'input_parameters': {
                    'height_m': height,
                    'dbh_m': dbh,
                    'latitude': latitude,
                    'longitude': longitude,
                    'species': species or 'Default Mixed Species',
                    'age_years': age
                },
                'biomass_analysis': {
                    'above_ground_biomass_kg': result['above_ground_biomass_kg'],
                    'below_ground_biomass_kg': result['below_ground_biomass_kg'],
                    'total_biomass_kg': result['total_biomass_kg'],
                    'carbon_content_kg': result['carbon_content_kg']
                },
                'carbon_sequestration': {
                    'total_co2_sequestered_tonnes': result['total_co2_sequestered_tonnes'],
                    'annual_co2_sequestration_tonnes': result['annual_co2_sequestration_tonnes'],
                    'climate_adjustment_factor': result['climate_factor'],
                    'wood_density_kg_per_m3': result['wood_density']
                },
                'environmental_impact': {
                    'equivalent_car_emissions_offset_days': round(result['total_co2_sequestered_tonnes'] * 365 / 4.6, 1),
                    'equivalent_tree_years': round(result['total_co2_sequestered_tonnes'] / 0.022, 1),
                    'economic_value_usd': round(result['total_co2_sequestered_tonnes'] * 15, 2)
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@ngo_bp.route("/camera/capture", methods=["POST"])
def camera_capture():
    """Handle real-time camera capture with geo-tagging"""
    try:
        # Get image data from request
        image_data = request.json.get('image_data')
        latitude = request.json.get('latitude')
        longitude = request.json.get('longitude')
        
        if not image_data:
            return jsonify({'success': False, 'error': 'No image data received'})
        
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        
        # Save image with location data
        filename = f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(UPLOADS_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Analyze the captured image
        species, carbon_rate, carbon_credits, error = predict_species_and_carbon(filepath)
        
        if error:
            return jsonify({'success': False, 'error': error})
        
        return jsonify({
            'success': True,
            'filename': filename,
            'analysis': {
                'species': species,
                'carbon_absorption_rate': round(carbon_rate, 2),
                'estimated_carbon_credits': round(carbon_credits, 2),
                'captured_location': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@ngo_bp.route("/credits")
def credits_view():
    generate_dummy_credits()  # Ensure we have data
    
    # Filter credits based on query parameters
    query = request.args.get('q', '')
    year = request.args.get('year', '')
    status = request.args.get('status', '')
    
    filtered_credits = credits_data
    if query:
        filtered_credits = [c for c in filtered_credits if query.lower() in c['project'].lower() or query in c['token']]
    if year:
        filtered_credits = [c for c in filtered_credits if c['vintage'] == int(year)]
    if status:
        filtered_credits = [c for c in filtered_credits if c['status'].lower() == status.lower()]
    
    # Calculate totals
    total_credits = sum(c['amount'] for c in credits_data)
    verified_credits = sum(c['amount'] for c in credits_data if c['verification'] == 'Verified')
    pending_credits = sum(c['amount'] for c in credits_data if c['verification'] == 'Pending')
    sold_credits = sum(c['amount'] for c in credits_data if c['status'] == 'Sold')
    total_revenue = sum(c['revenue'] for c in credits_data if c['status'] == 'Sold')
    
    stats = {
        'total_credits': total_credits,
        'verified_credits': verified_credits,
        'pending_credits': pending_credits,
        'sold_credits': sold_credits,
        'total_revenue': total_revenue
    }
    
    return render_template("ngo/credits.html", credits=filtered_credits, stats=stats)

@ngo_bp.route("/credits/export")
def export_credits_csv():
    generate_dummy_credits()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Project', 'Vintage', 'Credits (tCO2e)', 'Verification', 'Token ID', 'Status', 'Revenue (₹)', 'Date Created'])
    
    # Write data
    for credit in credits_data:
        writer.writerow([
            credit['project'],
            credit['vintage'],
            credit['amount'],
            credit['verification'],
            credit['token'],
            credit['status'],
            credit['revenue'],
            credit['date_created'].strftime('%Y-%m-%d')
        ])
    
    # Create response
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=credits_export_{datetime.now().strftime("%Y%m%d")}.csv'
    return response

@ngo_bp.route("/credits/realtime")
def credits_realtime():
    """API endpoint for real-time credits updates"""
    generate_dummy_credits()
    
    # Simulate real-time updates by occasionally modifying data
    if random.random() < 0.1:  # 10% chance to add new credit
        new_credit = {
            'id': len(credits_data) + 1,
            'project': random.choice(['New Mangrove Project', 'Seagrass Extension', 'Coastal Reforestation']),
            'vintage': 2024,
            'amount': random.randint(20, 200),
            'verification': 'Pending',
            'token': f"BC{random.randint(100000, 999999)}",
            'status': 'Available',
            'revenue': 0,
            'date_created': datetime.now()
        }
        credits_data.append(new_credit)
    
    return jsonify({
        'total_credits': len(credits_data),
        'latest_credits': credits_data[-5:] if credits_data else []
    })

@ngo_bp.route("/revenue")
def revenue_view():
    generate_dummy_transactions()  # Ensure we have data
    
    # Calculate summary
    total_revenue = sum(t['total'] for t in transactions_data if t['status'] == 'Completed')
    pending_transfer = sum(t['total'] for t in transactions_data if t['status'] == 'Processing')
    distributed = total_revenue * 0.8  # Assume 80% has been distributed
    credits_sold = sum(t['credits'] for t in transactions_data if t['status'] == 'Completed')
    avg_price = total_revenue / credits_sold if credits_sold > 0 else 0
    
    revenue_summary = {
        "total_revenue": int(total_revenue),
        "pending_transfer": int(pending_transfer),
        "distributed": int(distributed),
        "credits_sold": credits_sold,
        "avg_price": int(avg_price),
    }
    
    return render_template("ngo/revenue.html", transactions=transactions_data, summary=revenue_summary)

@ngo_bp.route("/revenue/request_payout", methods=["POST"])
def request_payout():
    amount = request.form.get('amount', 0)
    payment_method = request.form.get('payment_method', 'bank')
    
    # Create a new payout request
    payout_request = {
        'id': f"PAY{random.randint(100000, 999999)}",
        'amount': float(amount) if amount else random.randint(10000, 100000),
        'method': payment_method,
        'status': 'Pending',
        'requested_at': datetime.now(),
        'estimated_completion': datetime.now() + timedelta(days=3)
    }
    
    # Store payout request (in production, save to database)
    if 'payout_requests' not in globals():
        globals()['payout_requests'] = []
    globals()['payout_requests'].append(payout_request)
    
    if request.is_json:
        return jsonify({
            'success': True,
            'message': f'Payout request of ₹{payout_request["amount"]:,.0f} submitted successfully',
            'request_id': payout_request['id']
        })
    
    flash(f'Payout request of ₹{payout_request["amount"]:,.0f} submitted successfully!', 'success')
    return redirect(url_for('ngo.revenue_view'))

@ngo_bp.route("/revenue/realtime")
def revenue_realtime():
    """API endpoint for real-time revenue updates"""
    generate_dummy_transactions()
    
    # Simulate new transactions occasionally
    if random.random() < 0.05:  # 5% chance
        new_transaction = {
            'id': f"TXN{random.randint(100000, 999999)}",
            'project': random.choice(['Mangrove Restoration Chennai', 'Seagrass Conservation Kerala']),
            'credits': random.randint(10, 50),
            'price': random.randint(180, 250),
            'total': 0,  # Will be calculated
            'buyer': random.choice(['EcoTech Corp', 'Green Industries Ltd']),
            'date': datetime.now(),
            'status': 'Completed'
        }
        new_transaction['total'] = new_transaction['credits'] * new_transaction['price']
        transactions_data.append(new_transaction)
    
    recent_transactions = transactions_data[-3:] if transactions_data else []
    total_revenue = sum(t['total'] for t in transactions_data if t['status'] == 'Completed')
    
    return jsonify({
        'total_transactions': len(transactions_data),
        'total_revenue': total_revenue,
        'recent_transactions': [{
            'id': t['id'],
            'project': t['project'],
            'total': t['total'],
            'date': t['date'].strftime('%Y-%m-%d %H:%M') if isinstance(t['date'], datetime) else str(t['date'])
        } for t in recent_transactions]
    })

# Innovative Features - Analytics and Insights
@ngo_bp.route("/analytics")
def analytics_view():
    """Advanced analytics dashboard with environmental impact metrics"""
    generate_dummy_credits()
    generate_dummy_transactions()
    
    # Calculate environmental impact metrics
    total_co2_sequestered = sum(c['amount'] for c in credits_data)
    trees_equivalent = total_co2_sequestered * 18  # Approximate trees equivalent
    cars_offset = total_co2_sequestered * 0.23  # Cars taken off road for a year
    energy_savings = total_co2_sequestered * 1.2  # MWh of clean energy equivalent
    
    # Project success metrics
    project_success_rate = random.uniform(85, 95)
    community_engagement_score = random.uniform(4.2, 4.8)
    biodiversity_index = random.uniform(7.5, 9.2)
    
    # Monthly trends (last 12 months)
    monthly_credits = []
    monthly_revenue = []
    months = []
    
    for i in range(12):
        month_date = datetime.now() - timedelta(days=30*i)
        months.insert(0, month_date.strftime('%b %Y'))
        monthly_credits.insert(0, random.randint(50, 200))
        monthly_revenue.insert(0, random.randint(15000, 80000))
    
    analytics_data = {
        'environmental_impact': {
            'total_co2_sequestered': total_co2_sequestered,
            'trees_equivalent': int(trees_equivalent),
            'cars_offset': round(cars_offset, 1),
            'energy_savings': round(energy_savings, 1)
        },
        'project_metrics': {
            'success_rate': round(project_success_rate, 1),
            'community_engagement': round(community_engagement_score, 1),
            'biodiversity_index': round(biodiversity_index, 1)
        },
        'trends': {
            'months': months,
            'monthly_credits': monthly_credits,
            'monthly_revenue': monthly_revenue
        },
        'geographic_distribution': [
            {'region': 'Tamil Nadu', 'projects': 5, 'credits': 850},
            {'region': 'Kerala', 'projects': 4, 'credits': 720},
            {'region': 'Maharashtra', 'projects': 3, 'credits': 580}
        ]
    }
    
    return render_template("ngo/analytics.html", data=analytics_data)

@ngo_bp.route("/alerts")
def alerts_realtime():
    """Real-time alerts and notifications system"""
    alerts = [
        {
            'type': 'success',
            'title': 'Project Verification Complete',
            'message': 'Mangrove Restoration Project has been verified by NCCR',
            'timestamp': datetime.now() - timedelta(minutes=5),
            'priority': 'medium'
        },
        {
            'type': 'info',
            'title': 'New Credit Sale',
            'message': '150 carbon credits sold to EcoTech Corp',
            'timestamp': datetime.now() - timedelta(hours=2),
            'priority': 'low'
        },
        {
            'type': 'warning',
            'title': 'Document Expiry',
            'message': 'Project license expires in 30 days - renewal required',
            'timestamp': datetime.now() - timedelta(hours=6),
            'priority': 'high'
        }
    ]
    
    return jsonify({'alerts': [{
        'type': alert['type'],
        'title': alert['title'],
        'message': alert['message'],
        'timestamp': alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
        'priority': alert['priority']
    } for alert in alerts]})

@ngo_bp.route("/smart_insights")
def smart_insights():
    """AI-powered insights and recommendations"""
    insights = {
        'performance_insights': [
            {
                'category': 'Revenue Optimization',
                'insight': 'Your credit prices are 15% below market average. Consider gradual price increases.',
                'potential_impact': '+₹125,000 annual revenue',
                'confidence': 0.85
            },
            {
                'category': 'Project Efficiency',
                'insight': 'Projects in coastal areas show 23% higher carbon sequestration rates.',
                'potential_impact': 'Focus expansion on coastal regions',
                'confidence': 0.92
            },
            {
                'category': 'Seasonal Trends',
                'insight': 'Credit demand peaks during Q4. Plan marketing campaigns accordingly.',
                'potential_impact': '+35% Q4 sales potential',
                'confidence': 0.78
            }
        ],
        'predictive_analytics': {
            'next_quarter_credits': random.randint(180, 280),
            'revenue_forecast': random.randint(45000, 75000),
            'market_demand_trend': 'increasing',
            'optimal_pricing': random.randint(220, 280)
        },
        'risk_assessment': {
            'climate_risk': 'low',
            'market_volatility': 'medium',
            'regulatory_changes': 'low',
            'overall_risk_score': random.uniform(3.2, 4.1)
        }
    }
    
    return jsonify(insights)

@app.route("/_routes")
def list_routes():
    lines = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        lines.append(f"{methods}\t{rule.endpoint}\t{rule}")
    return Response("\n".join(sorted(lines)), mimetype="text/plain")

# Fallback direct routes in case blueprint isn't resolving
@app.route("/ngo/")
def _ngo_root_fallback():
    return redirect(url_for("ngo.dashboard_view"))

@app.route("/ngo/dashboard")
def _ngo_dashboard_fallback():
    return render_template("ngo/dashboard.html", stats={
        "total_projects": 0,
        "approved_projects": 0,
        "credits_earned": 0,
        "pending_verifications": 0,
        "reversed_applications": 0,
        "revenue_generated": 0,
    })

# NCCR Admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Admin data storage
admin_projects_data = []
admin_ngos_data = []
admin_industries_data = []
admin_transactions_data = []

def generate_admin_dummy_data():
    """Generate dummy data for admin panels"""
    global admin_projects_data, admin_ngos_data, admin_industries_data, admin_transactions_data
    
    if not admin_projects_data:
        # Sample projects for admin review
        for i in range(20):
            status = random.choice(['Pending Review', 'Documents Missing', 'Under Verification', 'Verified', 'Rejected'])
            admin_projects_data.append({
                'id': f'PROJ{1000 + i}',
                'name': random.choice(['Mangrove Restoration Sundarbans', 'Coastal Forest Tamil Nadu', 'Seagrass Conservation Kerala', 'Wetland Protection Odisha']),
                'ngo_name': random.choice(['Green Earth NGO', 'Coastal Conservation Trust', 'Marine Life Foundation', 'Blue Planet Initiative']),
                'location': random.choice(['West Bengal, Sundarbans', 'Tamil Nadu, Chennai', 'Kerala, Kochi', 'Odisha, Puri']),
                'ecosystem': random.choice(['Mangrove', 'Seagrass', 'Coastal Wetlands', 'Marine Forest']),
                'area': random.uniform(5, 100),
                'credits_requested': random.randint(100, 1000),
                'submission_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'status': status,
                'approval_date': datetime.now() - timedelta(days=random.randint(1, 30)) if status == 'Verified' else None,
                'token_id': f'TOKEN{random.randint(100000, 999999)}' if status == 'Verified' else None,
                'lat': random.uniform(8, 35),
                'lon': random.uniform(68, 97)
            })
    
    if not admin_ngos_data:
        # Sample NGOs
        for i in range(15):
            status = random.choice(['Verified', 'Pending', 'Blacklisted'])
            admin_ngos_data.append({
                'id': f'NGO{2000 + i}',
                'name': random.choice(['Green Earth Foundation', 'Coastal Conservation Trust', 'Marine Restoration NGO', 'Blue Carbon Initiative']),
                'location': random.choice(['Maharashtra, Mumbai', 'Tamil Nadu, Chennai', 'Kerala, Kochi', 'West Bengal, Kolkata']),
                'contact_person': random.choice(['Dr. Priya Sharma', 'Rajesh Kumar', 'Anita Patel', 'Suresh Reddy']),
                'contact_email': f'contact{i}@ngo{i}.org',
                'contact_phone': f'+91-{random.randint(9000000000, 9999999999)}',
                'status': status,
                'total_projects': random.randint(3, 25),
                'total_credits': random.randint(500, 5000),
                'total_revenue': random.randint(50000, 500000),
                'registration_number': f'NGO/REG/2020/{1000 + i}',
                'wallet_address': f'0x{random.randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):040x}',
                'bank_name': random.choice(['State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Axis Bank']),
                'registration_date': datetime.now() - timedelta(days=random.randint(30, 1000))
            })
    
    if not admin_industries_data:
        # Sample industries
        for i in range(12):
            status = random.choice(['Verified', 'Pending', 'Blacklisted'])
            admin_industries_data.append({
                'id': f'IND{3000 + i}',
                'name': random.choice(['Tata Steel Ltd', 'Reliance Industries', 'UltraTech Cement', 'TCS Limited', 'Infosys Technologies']),
                'sector': random.choice(['Steel', 'Oil & Gas', 'Cement', 'IT Services', 'Manufacturing']),
                'location': random.choice(['Maharashtra, Mumbai', 'Gujarat, Ahmedabad', 'Karnataka, Bangalore', 'Tamil Nadu, Chennai']),
                'contact_person': random.choice(['Amit Shah', 'Priya Nair', 'Vikram Singh', 'Neha Gupta']),
                'contact_email': f'sustainability{i}@industry{i}.com',
                'contact_phone': f'+91-{random.randint(9000000000, 9999999999)}',
                'status': status,
                'credits_purchased': random.randint(100, 2000),
                'revenue_contributed': random.randint(100000, 2000000),
                'registration_number': f'IND/REG/2020/{2000 + i}',
                'wallet_address': f'0x{random.randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):040x}',
                'registration_date': datetime.now() - timedelta(days=random.randint(30, 800))
            })
    
    if not admin_transactions_data:
        # Sample transactions
        for i in range(25):
            credits_sold = random.randint(10, 200)
            price_per_credit = random.randint(180, 350)
            admin_transactions_data.append({
                'id': f'TXN{random.randint(100000, 999999)}',
                'buyer': random.choice(['Tata Steel Ltd', 'Reliance Industries', 'UltraTech Cement', 'TCS Limited']),
                'seller': random.choice(['Green Earth Foundation', 'Coastal Conservation Trust', 'Marine Restoration NGO']),
                'credits_sold': credits_sold,
                'price_per_credit': price_per_credit,
                'total_value': credits_sold * price_per_credit,
                'transaction_date': datetime.now() - timedelta(days=random.randint(1, 180)),
                'status': random.choice(['Completed', 'Pending', 'Failed']),
                'token_id': f'TOKEN{random.randint(100000, 999999)}',
                'blockchain_hash': f'0x{random.randint(10**63, 10**64-1):064x}'
            })

@admin_bp.route("/")
def admin_dashboard():
    """NCCR Admin Dashboard"""
    generate_admin_dummy_data()
    
    # Calculate dashboard statistics
    total_projects = len(admin_projects_data)
    pending_verification = len([p for p in admin_projects_data if p['status'] in ['Pending Review', 'Documents Missing', 'Under Verification']])
    verified_projects = len([p for p in admin_projects_data if p['status'] == 'Verified'])
    total_credits_generated = sum(p['credits_requested'] for p in admin_projects_data)
    total_credits_verified = sum(p['credits_requested'] for p in admin_projects_data if p['status'] == 'Verified')
    total_revenue_distributed = sum(t['total_value'] for t in admin_transactions_data if t['status'] == 'Completed')
    
    # NGO statistics
    total_ngos = len(admin_ngos_data)
    verified_ngos = len([n for n in admin_ngos_data if n['status'] == 'Verified'])
    pending_ngos = len([n for n in admin_ngos_data if n['status'] == 'Pending'])
    blacklisted_ngos = len([n for n in admin_ngos_data if n['status'] == 'Blacklisted'])
    
    # Industry statistics
    total_industries = len(admin_industries_data)
    verified_industries = len([i for i in admin_industries_data if i['status'] == 'Verified'])
    pending_industries = len([i for i in admin_industries_data if i['status'] == 'Pending'])
    total_credits_purchased = sum(i['credits_purchased'] for i in admin_industries_data)
    total_revenue_generated = sum(i['revenue_contributed'] for i in admin_industries_data)
    
    # Recent activities
    recent_activities = [
        {'title': 'New project submitted for verification', 'time': '2 hours ago', 'type': 'info'},
        {'title': 'Credits issued to Green Earth Foundation', 'time': '4 hours ago', 'type': 'success'},
        {'title': 'Industry verification completed', 'time': '6 hours ago', 'type': 'success'},
        {'title': 'Transaction failed - requires attention', 'time': '1 day ago', 'type': 'warning'},
        {'title': 'New NGO registration pending', 'time': '2 days ago', 'type': 'info'}
    ]
    
    dashboard_stats = {
        'projects': {
            'total': total_projects,
            'pending_verification': pending_verification,
            'verified': verified_projects,
            'credits_generated': total_credits_generated,
            'credits_verified': total_credits_verified,
            'revenue_distributed': total_revenue_distributed
        },
        'ngos': {
            'total': total_ngos,
            'verified': verified_ngos,
            'pending': pending_ngos,
            'blacklisted': blacklisted_ngos
        },
        'industries': {
            'total': total_industries,
            'verified': verified_industries,
            'pending': pending_industries,
            'credits_purchased': total_credits_purchased,
            'revenue_generated': total_revenue_generated
        }
    }
    
    return render_template("admin/dashboard.html", stats=dashboard_stats, activities=recent_activities, now=datetime.now())

@admin_bp.route("/projects")
def projects_management():
    """Projects Management - Main View"""
    generate_admin_dummy_data()
    
    # Filter projects
    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '')
    
    filtered_projects = admin_projects_data
    if status_filter:
        filtered_projects = [p for p in filtered_projects if p['status'] == status_filter]
    if search_query:
        filtered_projects = [p for p in filtered_projects if search_query.lower() in p['name'].lower() or search_query.lower() in p['ngo_name'].lower()]
    
    return render_template("admin/projects.html", projects=filtered_projects, status_filter=status_filter, search_query=search_query)

@admin_bp.route("/projects/<project_id>")
def project_details(project_id):
    """Project Details View"""
    generate_admin_dummy_data()
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Get NGO details
    ngo = next((n for n in admin_ngos_data if n['name'] == project['ngo_name']), None)
    
    return render_template("admin/project_details.html", project=project, ngo=ngo)

@admin_bp.route("/projects/<project_id>/action", methods=["POST"])
def project_action(project_id):
    """Handle project actions (approve, reject, send back)"""
    generate_admin_dummy_data()
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    if action == 'approve':
        project['status'] = 'Verified'
        project['approval_date'] = datetime.now()
        project['token_id'] = f'TOKEN{random.randint(100000, 999999)}'
        message = f'Project {project_id} has been approved and credits issued.'
        
    elif action == 'reject':
        project['status'] = 'Rejected'
        project['rejection_reason'] = reason
        message = f'Project {project_id} has been rejected. Reason: {reason}'
        
    elif action == 'send_back':
        project['status'] = 'Documents Missing'
        project['revision_notes'] = reason
        message = f'Project {project_id} sent back for revision. Notes: {reason}'
    
    else:
        return jsonify({'success': False, 'error': 'Invalid action'}), 400
    
    if request.is_json:
        return jsonify({'success': True, 'message': message})
    
    flash(message, 'success')
    return redirect(url_for('admin.projects_management'))

@admin_bp.route("/revenue")
def revenue_tracking():
    """Revenue Tracking Dashboard"""
    generate_admin_dummy_data()
    
    # Calculate revenue statistics
    total_revenue = sum(t['total_value'] for t in admin_transactions_data if t['status'] == 'Completed')
    pending_payouts = sum(t['total_value'] for t in admin_transactions_data if t['status'] == 'Pending')
    failed_transactions = sum(t['total_value'] for t in admin_transactions_data if t['status'] == 'Failed')
    total_transactions = len(admin_transactions_data)
    
    revenue_stats = {
        'total_revenue': total_revenue,
        'pending_payouts': pending_payouts,
        'failed_transactions': failed_transactions,
        'total_transactions': total_transactions,
        'avg_transaction_value': total_revenue / total_transactions if total_transactions > 0 else 0
    }
    
    # Filter transactions
    status_filter = request.args.get('status', '')
    filtered_transactions = admin_transactions_data
    if status_filter:
        filtered_transactions = [t for t in filtered_transactions if t['status'] == status_filter]
    
    return render_template("admin/revenue.html", stats=revenue_stats, transactions=filtered_transactions, status_filter=status_filter)

@admin_bp.route("/ngos")
def ngos_management():
    """NGO Management Dashboard"""
    generate_admin_dummy_data()
    
    # Filter and search NGOs
    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '')
    
    filtered_ngos = admin_ngos_data
    if status_filter:
        filtered_ngos = [n for n in filtered_ngos if n['status'] == status_filter]
    if search_query:
        filtered_ngos = [n for n in filtered_ngos if search_query.lower() in n['name'].lower() or search_query.lower() in n['id'].lower()]
    
    # NGO statistics
    ngo_stats = {
        'total_ngos': len(admin_ngos_data),
        'verified_ngos': len([n for n in admin_ngos_data if n['status'] == 'Verified']),
        'pending_ngos': len([n for n in admin_ngos_data if n['status'] == 'Pending']),
        'blacklisted_ngos': len([n for n in admin_ngos_data if n['status'] == 'Blacklisted'])
    }
    
    return render_template("admin/ngos.html", ngos=filtered_ngos, stats=ngo_stats, status_filter=status_filter, search_query=search_query)

@admin_bp.route("/ngos/<ngo_id>")
def ngo_details(ngo_id):
    """NGO Details View"""
    generate_admin_dummy_data()
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        return jsonify({'error': 'NGO not found'}), 404
    
    # Get NGO's projects
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    
    return render_template("admin/ngo_details.html", ngo=ngo, projects=ngo_projects)

@admin_bp.route("/ngos/<ngo_id>/action", methods=["POST"])
def ngo_action(ngo_id):
    """Handle NGO actions (verify, blacklist, edit)"""
    generate_admin_dummy_data()
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        return jsonify({'success': False, 'error': 'NGO not found'}), 404
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    if action == 'verify':
        ngo['status'] = 'Verified'
        message = f'NGO {ngo["name"]} has been verified.'
        
    elif action == 'blacklist':
        ngo['status'] = 'Blacklisted'
        ngo['blacklist_reason'] = reason
        message = f'NGO {ngo["name"]} has been blacklisted. Reason: {reason}'
        
    else:
        return jsonify({'success': False, 'error': 'Invalid action'}), 400
    
    if request.is_json:
        return jsonify({'success': True, 'message': message})
    
    flash(message, 'success')
    return redirect(url_for('admin.ngos_management'))

@admin_bp.route("/industries")
def industries_management():
    """Industries Management Dashboard"""
    generate_admin_dummy_data()
    
    # Filter and search industries
    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '')
    
    filtered_industries = admin_industries_data
    if status_filter:
        filtered_industries = [i for i in filtered_industries if i['status'] == status_filter]
    if search_query:
        filtered_industries = [i for i in filtered_industries if search_query.lower() in i['name'].lower() or search_query.lower() in i['id'].lower()]
    
    # Industry statistics
    industry_stats = {
        'total_industries': len(admin_industries_data),
        'verified_buyers': len([i for i in admin_industries_data if i['status'] == 'Verified']),
        'pending_approval': len([i for i in admin_industries_data if i['status'] == 'Pending']),
        'total_credits_purchased': sum(i['credits_purchased'] for i in admin_industries_data),
        'total_revenue_generated': sum(i['revenue_contributed'] for i in admin_industries_data)
    }
    
    return render_template("admin/industries.html", industries=filtered_industries, stats=industry_stats, status_filter=status_filter, search_query=search_query)

@admin_bp.route("/industries/<industry_id>")
def industry_details(industry_id):
    """Industry Details View"""
    generate_admin_dummy_data()
    
    industry = next((i for i in admin_industries_data if i['id'] == industry_id), None)
    if not industry:
        return jsonify({'error': 'Industry not found'}), 404
    
    # Get industry's purchase history
    industry_transactions = [t for t in admin_transactions_data if t['buyer'] == industry['name']]
    
    return render_template("admin/industry_details.html", industry=industry, transactions=industry_transactions)

@admin_bp.route("/industries/<industry_id>/action", methods=["POST"])
def industry_action(industry_id):
    """Handle industry actions (verify, blacklist, edit)"""
    generate_admin_dummy_data()
    
    industry = next((i for i in admin_industries_data if i['id'] == industry_id), None)
    if not industry:
        return jsonify({'success': False, 'error': 'Industry not found'}), 404
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    if action == 'verify':
        industry['status'] = 'Verified'
        message = f'Industry {industry["name"]} has been verified.'
        
    elif action == 'blacklist':
        industry['status'] = 'Blacklisted'
        industry['blacklist_reason'] = reason
        message = f'Industry {industry["name"]} has been blacklisted. Reason: {reason}'
        
    else:
        return jsonify({'success': False, 'error': 'Invalid action'}), 400
    
    if request.is_json:
        return jsonify({'success': True, 'message': message})
    
    flash(message, 'success')
    return redirect(url_for('admin.industries_management'))

@admin_bp.route("/export/<data_type>")
def export_data(data_type):
    """Export data to CSV"""
    generate_admin_dummy_data()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if data_type == 'projects':
        writer.writerow(['Project ID', 'Name', 'NGO', 'Location', 'Ecosystem', 'Area (ha)', 'Credits Requested', 'Status', 'Submission Date'])
        for project in admin_projects_data:
            writer.writerow([
                project['id'], project['name'], project['ngo_name'], project['location'],
                project['ecosystem'], project['area'], project['credits_requested'],
                project['status'], project['submission_date'].strftime('%Y-%m-%d')
            ])
        filename = f'nccr_projects_{datetime.now().strftime("%Y%m%d")}.csv'
        
    elif data_type == 'ngos':
        writer.writerow(['NGO ID', 'Name', 'Location', 'Contact Person', 'Status', 'Total Projects', 'Total Credits', 'Registration Date'])
        for ngo in admin_ngos_data:
            writer.writerow([
                ngo['id'], ngo['name'], ngo['location'], ngo['contact_person'],
                ngo['status'], ngo['total_projects'], ngo['total_credits'],
                ngo['registration_date'].strftime('%Y-%m-%d')
            ])
        filename = f'nccr_ngos_{datetime.now().strftime("%Y%m%d")}.csv'
        
    elif data_type == 'industries':
        writer.writerow(['Industry ID', 'Name', 'Sector', 'Location', 'Status', 'Credits Purchased', 'Revenue Contributed', 'Registration Date'])
        for industry in admin_industries_data:
            writer.writerow([
                industry['id'], industry['name'], industry['sector'], industry['location'],
                industry['status'], industry['credits_purchased'], industry['revenue_contributed'],
                industry['registration_date'].strftime('%Y-%m-%d')
            ])
        filename = f'nccr_industries_{datetime.now().strftime("%Y%m%d")}.csv'
        
    else:
        return jsonify({'error': 'Invalid data type'}), 400
    
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# Register blueprints
app.register_blueprint(ngo_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)
