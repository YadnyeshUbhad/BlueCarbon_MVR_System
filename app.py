from flask import Flask, request, Response, render_template, redirect, url_for, jsonify, session, flash
from flask import Blueprint
import os
import json
import csv
import io
import base64
from datetime import datetime, timedelta
import random
import uuid
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import hashlib
import time
from datetime import datetime, timedelta
import json
from blockchain_sim import blockchain_mrv
from real_satellite_apis import real_satellite_integration
from ml_predictions import ml_predictor
from drone_processing import drone_processor
from geospatial_analysis import geospatial_analyzer
from token_visualization import token_viz_engine
from location_manager import location_manager
from auth import login_required, authenticate_user, login_user, logout_user, get_current_user
from db import init_db, save_token, save_transaction, get_conn
from werkzeug.security import generate_password_hash
from production_config import (
    production_config, production_database, external_apis, 
    production_monitoring, initialize_production_services, 
    is_production, get_database_connection, get_api_client, record_metric,
    get_metrics, get_integration_config, is_feature_enabled
)
# from supabase_client import supabase_client  # Replaced with Firebase
from firebase_client import firebase_client
from email_notifications import email_system
from mrv_workflow_system import mrv_workflow_engine
from blockchain_routes import blockchain_bp
from real_blockchain_routes import real_blockchain_bp
from research_dashboard import research_bp
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-please-change-this')

# Disable template caching in development to prevent template confusion
if not is_production():
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}

# Configure application logger for use throughout the app
logger: logging.Logger = app.logger
logger.setLevel(logging.INFO)

# Add Jinja2 custom functions
from datetime import datetime as dt

@app.template_global()
def now():
    return dt.now()

@app.template_filter()
def to_datetime(value):
    if isinstance(value, str):
        try:
            return dt.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return dt.now()
    return value

# Initialize database on startup
init_db()

# Create uploads directory if it doesn't exist
UPLOADS_FOLDER = 'uploads'
if not os.path.exists(UPLOADS_FOLDER):
    os.makedirs(UPLOADS_FOLDER)

# In-memory data storage (in production, use a proper database)
admin_projects_data = []
admin_ngos_data = []
admin_industries_data = []
transactions_data = []

def generate_comprehensive_admin_data():
    """Generate comprehensive dummy data for admin system"""
    global admin_projects_data, admin_ngos_data, admin_industries_data, transactions_data
    
    if not admin_projects_data:
        # Generate projects with detailed information
        project_names = [
            'Sundarbans Mangrove Restoration', 'Chennai Coastal Forest Revival', 
            'Kerala Seagrass Conservation', 'Odisha Wetland Protection',
            'Mumbai Coastal Reforestation', 'Goa Mangrove Plantation',
            'Tamil Nadu Blue Carbon Initiative', 'West Bengal Coastal Guard',
            'Karnataka Marine Forest', 'Gujarat Coastal Conservation'
        ]
        
        ngo_names = [
            'Green Earth Foundation', 'Coastal Conservation Trust', 
            'Marine Life Protection Society', 'Blue Planet Initiative',
            'Ocean Guardians NGO', 'Coastal Development Trust',
            'Environmental Action Group', 'Sea Life Conservation'
        ]
        
        locations = [
            ('West Bengal', 'Sundarbans'), ('Tamil Nadu', 'Chennai'),
            ('Kerala', 'Kochi'), ('Odisha', 'Puri'),
            ('Maharashtra', 'Mumbai'), ('Goa', 'Panaji'),
            ('Karnataka', 'Mangalore'), ('Gujarat', 'Surat')
        ]
        
        ecosystems = ['Mangrove', 'Seagrass', 'Coastal Wetlands', 'Marine Forest', 'Coral Reef']
        
        for i in range(25):
            status = random.choice(['Pending Review', 'Documents Missing', 'Under Verification', 'Verified', 'Rejected'])
            state, district = random.choice(locations)
            
            project = {
                'id': f'PROJ{1000 + i}',
                'name': random.choice(project_names),
                'ngo_name': random.choice(ngo_names),
                'ngo_id': f'NGO{2000 + random.randint(0, 7)}',
                'state': state,
                'district': district,
                'location': f'{district}, {state}',
                'ecosystem': random.choice(ecosystems),
                'area': round(random.uniform(5.0, 150.0), 2),
                'credits_requested': random.randint(50, 800),
                'credits_approved': random.randint(30, 700) if status == 'Verified' else 0,
                'status': status,
                'submission_date': datetime.now() - timedelta(days=random.randint(1, 180)),
                'approval_date': datetime.now() - timedelta(days=random.randint(1, 30)) if status == 'Verified' else None,
                'token_id': f'BC{random.randint(100000, 999999)}' if status == 'Verified' else None,
                'verification_notes': f'Verification notes for project {i+1}' if status != 'Pending Review' else '',
                'last_updated': datetime.now() - timedelta(days=random.randint(0, 30)),
                'contact_person': f'Contact Person {i+1}',
                'phone': f'+91-{random.randint(7000000000, 9999999999)}',
                'email': f'project{i+1}@{random.choice(ngo_names).lower().replace(" ", "")}.org',
                'documents': ['Registration Certificate', 'Project Proposal', 'Environmental Impact Assessment']
            }
            admin_projects_data.append(project)
    
    if not admin_ngos_data:
        # Generate NGOs with detailed information
        ngo_names = [
            'Green Earth Foundation', 'Coastal Conservation Trust', 
            'Marine Life Protection Society', 'Blue Planet Initiative',
            'Ocean Guardians NGO', 'Coastal Development Trust',
            'Environmental Action Group', 'Sea Life Conservation',
            'Nature Preservation Society', 'Eco Warriors Foundation'
        ]
        
        for i, name in enumerate(ngo_names):
            # Ensure first 3 NGOs are verified for testing, others can be random
            if i < 3:
                status = 'Verified'
            else:
                status = random.choice(['Verified', 'Pending', 'Blacklisted'])
            projects_count = len([p for p in admin_projects_data if p['ngo_name'] == name])
            credits_earned = sum(p['credits_approved'] for p in admin_projects_data if p['ngo_name'] == name)
            
            # For the first NGO, use test account email for authentication testing
            if i == 0:
                email = 'ngo@example.org'
                contact_person = 'Test NGO User'
            else:
                email = f'contact@{name.lower().replace(" ", "")}.org'
                contact_person = f'Director {i+1}'
            
            ngo = {
                'id': f'NGO{2000 + i}',
                'name': name,
                'registration_number': f'NGO/REG/2020/{1000 + i}',
                'status': status,
                'contact_person': contact_person,
                'phone': f'+91-{random.randint(7000000000, 9999999999)}',
                'email': email,
                'address': f'{random.randint(100, 999)} {name} Building, {random.choice(["Marine Drive", "Coastal Road", "Ocean View"])}',
                'state': random.choice(['Maharashtra', 'Tamil Nadu', 'Kerala', 'West Bengal', 'Odisha']),
                'district': random.choice(['Mumbai', 'Chennai', 'Kochi', 'Kolkata', 'Puri']),
                'bank_name': random.choice(['State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Punjab National Bank']),
                'account_number': f'**********{random.randint(1000, 9999)}',
                'ifsc_code': f'{random.choice(["SBIN", "HDFC", "ICIC", "PUNB"])}000{random.randint(1000, 9999)}',
                'wallet_address': f'0x{random.randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):040x}',
                'projects_submitted': projects_count,
                'credits_earned': credits_earned,
                'total_revenue': credits_earned * random.randint(180, 250),
                'registration_date': datetime.now() - timedelta(days=random.randint(100, 1200)),
                'verification_date': datetime.now() - timedelta(days=random.randint(1, 100)) if status == 'Verified' else None,
                'documents': ['Registration Certificate', 'Tax Exemption Certificate', 'Bank Account Proof']
            }
            admin_ngos_data.append(ngo)
    
    if not admin_industries_data:
        # Generate Industries with detailed information
        company_names = [
            'EcoTech Industries Ltd', 'Green Manufacturing Corp', 'Carbon Offset Solutions',
            'CleanTech International', 'Sustainable Industries Group', 'Zero Carbon Ltd',
            'Environmental Solutions Inc', 'Green Energy Corporation', 'Eco-Friendly Manufacturing',
            'Carbon Neutral Industries', 'Clean Production Ltd', 'Sustainable Tech Corp',
            'Green Innovation Ltd', 'Eco Industries Group', 'Climate Solutions Inc'
        ]
        
        sectors = ['Manufacturing', 'Technology', 'Energy', 'Transportation', 'Cement', 'Steel', 'IT', 'FMCG', 'Pharmaceuticals', 'Textiles']
        
        for i, name in enumerate(company_names):
            # Ensure first 2 industries are verified for testing
            if i < 2:
                status = 'Verified'
            else:
                status = random.choice(['Verified', 'Pending'])
            credits_purchased = random.randint(100, 2000)
            price_per_credit = random.randint(180, 280)
            revenue_contributed = credits_purchased * price_per_credit
            
            # For the first industry, use test account email
            if i == 0:
                email = 'industry@example.com'
                contact_person = 'Test Industry User'
            else:
                email = f'contact@{name.lower().replace(" ", "").replace("ltd", "").replace("corp", "").replace("inc", "")}'
                contact_person = f'Manager {i+1}'
            
            industry = {
                'id': f'IND{3000 + i}',
                'name': name,
                'sector': random.choice(sectors),
                'registration_number': f'IND/REG/{random.randint(100000, 999999)}',
                'status': status,
                'contact_person': contact_person,
                'phone': f'+91-{random.randint(7000000000, 9999999999)}',
                'email': email,
                'address': f'{random.randint(100, 999)} Industrial Area, {random.choice(["Sector", "Phase", "Block"])} {random.randint(1, 50)}',
                'city': random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Pune', 'Hyderabad']),
                'state': random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Telangana']),
                'wallet_address': f'0x{random.randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):040x}',
                'bank_name': random.choice(['HDFC Bank', 'ICICI Bank', 'Axis Bank', 'State Bank of India']),
                'account_number': f'**********{random.randint(1000, 9999)}',
                'credits_purchased': credits_purchased,
                'revenue_contributed': revenue_contributed,
                'registration_date': datetime.now() - timedelta(days=random.randint(50, 800)),
                'verification_date': datetime.now() - timedelta(days=random.randint(1, 50)) if status == 'Verified' else None,
                'purchase_history': []
            }
            
            # Generate purchase history
            for j in range(random.randint(2, 8)):
                purchase = {
                    'transaction_id': f'TXN{random.randint(100000, 999999)}',
                    'project_name': random.choice([p['name'] for p in admin_projects_data[:10]]),
                    'credits_bought': random.randint(10, 200),
                    'price_per_credit': random.randint(180, 280),
                    'total_amount': 0,  # Will be calculated
                    'purchase_date': datetime.now() - timedelta(days=random.randint(1, 180)),
                    'token_id': f'BC{random.randint(100000, 999999)}',
                    'status': random.choice(['Completed', 'Pending', 'Processing'])
                }
                purchase['total_amount'] = purchase['credits_bought'] * purchase['price_per_credit']
                industry['purchase_history'].append(purchase)
            
            admin_industries_data.append(industry)
    
    if not transactions_data:
        # Generate comprehensive transaction data
        for i in range(50):
            industry = random.choice(admin_industries_data)
            project = random.choice([p for p in admin_projects_data if p['status'] == 'Verified'])
            credits = random.randint(10, 150)
            price = random.randint(180, 280)
            
            transaction = {
                'id': f'TXN{100000 + i}',
                'project_name': project['name'],
                'project_id': project['id'],
                'ngo_name': project['ngo_name'],
                'buyer_name': industry['name'],
                'buyer_id': industry['id'],
                'credits_sold': credits,
                'price_per_credit': price,
                'total_value': credits * price,
                'transaction_date': datetime.now() - timedelta(days=random.randint(1, 120)),
                'status': random.choice(['Completed', 'Pending', 'Processing', 'Failed']),
                'token_id': f'BC{random.randint(100000, 999999)}',
                'blockchain_hash': f'0x{random.randint(1000000000000000, 9999999999999999):016x}'
            }
            transactions_data.append(transaction)

# NCCR Admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password, 'admin')
        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid credentials or access denied.', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

def get_role_specific_initial_data(org_type):
    """Get role-specific initial data based on organization type"""
    if org_type == 'ngo':
        return {
            'focus_areas': ['Environmental Conservation', 'Climate Change', 'Sustainability'],
            'operational_scale': 'Regional',
            'target_beneficiaries': 'Communities',
            'primary_activities': ['Project Implementation', 'Community Engagement', 'Research'],
            'certification_level': 'Basic',
            'capacity_score': 50,
            'max_project_size': 100,  # hectares
            'preferred_ecosystems': ['Mangrove', 'Coastal Wetlands']
        }
    elif org_type == 'panchayat':
        return {
            'administrative_level': 'Village',
            'population_served': 0,
            'governance_type': 'Democratic',
            'primary_activities': ['Local Governance', 'Rural Development', 'Environmental Management'],
            'jurisdiction_area': 0,  # square km
            'budget_allocation': 0,
            'development_priority': 'Environmental Conservation',
            'community_participation_score': 0,
            'max_project_size': 50,  # hectares
            'preferred_ecosystems': ['Coastal Wetlands', 'Mangrove']
        }
    elif org_type == 'cooperative':
        return {
            'membership_count': 0,
            'cooperative_type': 'Environmental',
            'economic_activities': ['Carbon Credit Trading', 'Sustainable Practices'],
            'annual_turnover': 0,
            'member_benefits': ['Revenue Sharing', 'Capacity Building'],
            'governance_model': 'Member-driven',
            'financial_capacity': 'Growing',
            'market_reach': 'Local',
            'max_project_size': 75,  # hectares
            'preferred_ecosystems': ['Mangrove', 'Seagrass']
        }
    elif org_type == 'community':
        return {
            'community_size': 0,
            'geographic_scope': 'Local',
            'primary_livelihood': 'Agriculture/Fishing',
            'organization_maturity': 'Emerging',
            'leadership_structure': 'Community-elected',
            'resource_access': 'Limited',
            'technical_capacity': 'Basic',
            'external_support_needed': True,
            'max_project_size': 25,  # hectares
            'preferred_ecosystems': ['Mangrove', 'Coastal Wetlands']
        }
    else:
        return {
            'organization_category': 'Other',
            'operational_focus': 'Environmental',
            'capacity_level': 'Basic',
            'max_project_size': 50,  # hectares
            'preferred_ecosystems': ['Mangrove']
        }

# NGO blueprint
ngo_bp = Blueprint("ngo", __name__, url_prefix="/ngo")

@ngo_bp.route("/")
def ngo_index():
    """NGO Portal Landing Page"""
    return render_template('ngo/index.html')

@ngo_bp.route("/home")
def ngo_home():
    return redirect(url_for("ngo.dashboard_view"))

@ngo_bp.route("/register", methods=['GET', 'POST'])
def ngo_register():
    """NGO Registration"""
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Organization details
            org_type = request.form.get('org_type', 'ngo')
            registration_number = request.form.get('registration_number', '').strip()
            contact_person = request.form.get('contact_person', '').strip()
            contact_phone = request.form.get('contact_phone', '').strip()
            address = request.form.get('address', '').strip()
            district = request.form.get('district', '').strip()
            state = request.form.get('state', '').strip()
            
            # Financial details
            payment_method = request.form.get('payment_method', 'bank')
            bank_name = request.form.get('bank_name', '').strip()
            account_number = request.form.get('account_number', '').strip()
            ifsc_code = request.form.get('ifsc_code', '').strip()
            account_holder_name = request.form.get('account_holder_name', '').strip()
            wallet_address = request.form.get('wallet_address', '').strip()
            
            # Validation
            if not all([name, email, password, contact_person, contact_phone]):
                flash('Please fill in all required fields.', 'error')
                return render_template('ngo/register.html')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('ngo/register.html')
            
            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('ngo/register.html')
            
            # Check if email already exists
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                flash('Email already registered. Please use a different email or login.', 'error')
                conn.close()
                return render_template('ngo/register.html')
            
            # Create new NGO user
            password_hash = generate_password_hash(password)
            now = datetime.utcnow().isoformat()
            
            cur.execute(
                "INSERT INTO users (email, password_hash, role, name, organization, created_at) VALUES (?,?,?,?,?,?)",
                (email, password_hash, 'ngo', contact_person, name, now)
            )
            conn.commit()
            
            # Generate appropriate ID based on organization type
            if org_type == 'ngo':
                new_id = f'NGO{2000 + len([n for n in admin_ngos_data if n.get("type", "ngo") == "ngo"])}'
            elif org_type == 'panchayat':
                new_id = f'PAN{3000 + len([n for n in admin_ngos_data if n.get("type", "ngo") == "panchayat"])}'
            elif org_type == 'cooperative':
                new_id = f'COOP{4000 + len([n for n in admin_ngos_data if n.get("type", "ngo") == "cooperative"])}'
            elif org_type == 'community':
                new_id = f'COMM{5000 + len([n for n in admin_ngos_data if n.get("type", "ngo") == "community"])}'
            else:
                new_id = f'ORG{6000 + len(admin_ngos_data)}'
            
            # Create role-specific registration data with proper zero initialization
            ngo_data = {
                'id': new_id,
                'name': name,
                'type': org_type,  # Store organization type
                'registration_number': registration_number,
                'status': 'Pending',  # Requires admin approval
                'contact_person': contact_person,
                'phone': contact_phone,
                'email': email,
                'address': address,
                'state': state,
                'district': district,
                'bank_name': bank_name,
                'account_number': account_number,
                'ifsc_code': ifsc_code,
                'wallet_address': wallet_address or f'0x{random.randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):040x}',
                # Initialize all financial metrics to zero for new organizations
                'projects_submitted': 0,
                'projects_verified': 0,
                'projects_pending': 0,
                'projects_rejected': 0,
                'credits_earned': 0,
                'credits_pending': 0,
                'total_revenue': 0,
                'available_balance': 0,
                'total_withdrawn': 0,
                'average_project_value': 0,
                'success_rate': 0.0,
                'last_project_date': None,
                'last_payment_date': None,
                'verification_score': 0,
                'community_impact_score': 0,
                'registration_date': datetime.now(),
                'verification_date': None,
                'last_activity_date': datetime.now(),
                'documents': ['Registration Form'],
                # Role-specific fields
                'role_specific_data': get_role_specific_initial_data(org_type)
            }
            admin_ngos_data.append(ngo_data)
            
            conn.close()
            
            # Send registration confirmation email
            try:
                email_system.send_ngo_registration_confirmation(
                    email=email,
                    name=contact_person,
                    org_name=name
                )
                logger.info(f"Registration confirmation email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send registration confirmation email: {e}")
            
            flash('Registration successful! Your account is pending admin approval. You will be notified once approved.', 'success')
            return redirect(url_for('ngo.ngo_login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('ngo/register.html')
    
    return render_template('ngo/register.html')

@ngo_bp.route("/login", methods=['GET', 'POST'])
def ngo_login():
    """NGO Login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password, 'ngo')
        if user:
            # Check if NGO is approved
            ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == email), None)
            
            if ngo_data and ngo_data['status'] == 'Blacklisted':
                flash('Your account has been suspended. Please contact support.', 'error')
                return render_template('ngo/login.html')
            elif ngo_data and ngo_data['status'] == 'Pending':
                flash('Your account is still pending admin approval. Please wait for verification.', 'warning')
                return render_template('ngo/login.html')
            
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('ngo.dashboard_view'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('ngo/login.html')

@ngo_bp.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public_landing_page'))

@ngo_bp.route("/dashboard")
@login_required(['ngo'])
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
    
    return render_template('ngo/dashboard.html', ngo=ngo, stats=stats, projects=ngo_projects[:5], recent_activities=recent_activities, active='dashboard')

@ngo_bp.route("/profile")
@login_required(['ngo'])
def ngo_profile():
    """NGO Profile Page"""
    generate_comprehensive_admin_data()
    
    # Check if NGO is approved
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data or ngo_data['status'] != 'Verified':
        flash('Access denied. Your NGO registration is pending admin approval.', 'warning')
        logout_user()
        return redirect(url_for('ngo.ngo_login'))
    ngo = ngo_data
    
    # Create profile object with all needed fields from template
    profile = {
        'name': ngo.get('name', 'Demo NGO'),
        'join_date': ngo.get('registration_date', datetime(2024, 1, 1)).strftime('%Y') if isinstance(ngo.get('registration_date'), datetime) else '2024',
        'total_projects': ngo.get('projects_submitted', 0),
        'total_credits': ngo.get('credits_earned', 0),
        'total_revenue': ngo.get('total_revenue', 0),
        'type': 'ngo',
        'registration_number': ngo.get('registration_number', ''),
        'contact_person': ngo.get('contact_person', ''),
        'contact_phone': ngo.get('phone', ''),
        'email': ngo.get('email', ''),
        'address': ngo.get('address', ''),
        'district': ngo.get('district', ''),
        'state': ngo.get('state', ''),
        'payment_method': 'bank',  # Default
        'bank_name': ngo.get('bank_name', ''),
        'account_number': ngo.get('account_number', ''),
        'ifsc_code': ngo.get('ifsc_code', ''),
        'account_holder_name': ngo.get('contact_person', ''),
        'wallet_address': ngo.get('wallet_address', ''),
        'wallet_type': 'metamask',  # Default
        'two_factor_enabled': False  # Default
    }
    
    return render_template('ngo/profile.html', profile=profile, ngo=ngo, active='profile')

@ngo_bp.route("/profile", methods=['POST'])
@login_required(['ngo'])
def update_ngo_profile():
    """Update NGO profile information"""
    generate_comprehensive_admin_data()
    
    # Check if NGO is approved
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data:
        return jsonify({'success': False, 'message': 'NGO not found'})
    
    try:
        # Update NGO data
        ngo_data['contact_person'] = request.form.get('contact_person', ngo_data['contact_person'])
        ngo_data['phone'] = request.form.get('contact_phone', ngo_data['phone'])
        ngo_data['address'] = request.form.get('address', ngo_data['address'])
        ngo_data['bank_name'] = request.form.get('bank_name', ngo_data['bank_name'])
        ngo_data['account_number'] = request.form.get('account_number', ngo_data['account_number'])
        ngo_data['ifsc_code'] = request.form.get('ifsc_code', ngo_data['ifsc_code'])
        ngo_data['wallet_address'] = request.form.get('wallet_address', ngo_data['wallet_address'])
        
        # Handle two-factor authentication toggle
        two_factor_enabled = request.form.get('two_factor_enabled') == 'on'
        ngo_data['two_factor_enabled'] = two_factor_enabled
        
        if two_factor_enabled and not ngo_data.get('two_factor_setup'):
            # Generate QR code and setup key for first time setup
            import secrets
            setup_key = secrets.token_hex(16)
            ngo_data['two_factor_setup_key'] = setup_key
            ngo_data['two_factor_setup'] = False
            
            return jsonify({
                'success': True, 
                'message': 'Profile updated successfully! Two-factor authentication setup initiated.',
                'two_factor_setup': True,
                'setup_key': setup_key
            })
        
        return jsonify({
            'success': True, 
            'message': 'Profile updated successfully!'
        })
        
    except Exception as e:
        logger.error(f"Failed to update NGO profile: {e}")
        return jsonify({'success': False, 'message': 'Failed to update profile. Please try again.'})

@ngo_bp.route("/2fa/setup", methods=['POST'])
@login_required(['ngo'])
def setup_2fa():
    """Setup Two-Factor Authentication for NGO"""
    try:
        user_email = session.get('user_email')
        ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
        
        if not ngo_data:
            return jsonify({'success': False, 'message': 'NGO not found'})
        
        # Generate secret key for 2FA
        import secrets
        secret_key = secrets.token_hex(16)
        ngo_data['two_factor_secret'] = secret_key
        
        # Generate QR code (simulated - in production use actual QR code library)
        qr_code_data = f"otpauth://totp/BlueCarbon:{user_email}?secret={secret_key}&issuer=BlueCarbon"
        
        # In production, generate actual QR code image
        qr_code_url = f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzMzMyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPjJGQSBTZXR1cCBRUiBDb2RlPC90ZXh0Pjwvc3ZnPg=="
        
        return jsonify({
            'success': True,
            'qr_code': qr_code_url,
            'secret': secret_key,
            'message': '2FA setup initiated successfully'
        })
        
    except Exception as e:
        logger.error(f"2FA setup error: {e}")
        return jsonify({'success': False, 'message': 'Failed to setup 2FA'})

@ngo_bp.route("/2fa/enable", methods=['POST'])
@login_required(['ngo'])
def enable_2fa():
    """Enable Two-Factor Authentication after verification"""
    try:
        user_email = session.get('user_email')
        ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
        
        if not ngo_data:
            return jsonify({'success': False, 'message': 'NGO not found'})
        
        verification_code = request.json.get('code')
        
        if not verification_code or len(verification_code) != 6:
            return jsonify({'success': False, 'message': 'Invalid verification code'})
        
        # In production, verify the TOTP code against the secret
        # For demo, accept any 6-digit code
        if verification_code.isdigit():
            ngo_data['two_factor_enabled'] = True
            ngo_data['two_factor_setup'] = True
            
            return jsonify({
                'success': True,
                'message': 'Two-Factor Authentication enabled successfully!'
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid verification code'})
        
    except Exception as e:
        logger.error(f"2FA enable error: {e}")
        return jsonify({'success': False, 'message': 'Failed to enable 2FA'})

@ngo_bp.route("/revenue")
@login_required(['ngo'])
def revenue_view():
    # Generate dummy transactions data
    transactions_data = []
    for i in range(6):
        transactions_data.append({
            'id': f"TXN{random.randint(100000, 999999)}",
            'project': f'Project {i+1}',
            'credits': random.randint(10, 50),
            'price': random.randint(180, 250),
            'total': random.randint(10000, 50000),
            'buyer': f'Buyer Company {i+1}',
            'date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'status': random.choice(['Completed', 'Processing', 'Pending'])
        })
    
    # Calculate summary
    total_revenue = sum(t['total'] for t in transactions_data if t['status'] == 'Completed')
    pending_transfer = sum(t['total'] for t in transactions_data if t['status'] == 'Processing')
    distributed = total_revenue * 0.8  # Assume 80% has been distributed
    credits_sold = sum(t['credits'] for t in transactions_data if t['status'] == 'Completed')
    avg_price = total_revenue / credits_sold if credits_sold > 0 else 0
    
    summary = {
        "total_revenue": int(total_revenue),
        "pending_transfer": int(pending_transfer),
        "distributed": int(distributed),
        "credits_sold": credits_sold,
        "avg_price": int(avg_price),
    }
    
    return render_template("ngo/revenue.html", transactions=transactions_data, summary=summary)

@ngo_bp.route("/profile", methods=["GET", "POST"])
@login_required(['ngo'])
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
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('ngo.profile_view'))
    
    # GET request - show profile
    profile = {
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
    }
    return render_template("ngo/profile.html", profile=profile)

@ngo_bp.route("/revenue/withdraw", methods=['POST'])
@login_required(['ngo'])
def withdraw_revenue():
    """Process NGO revenue withdrawal"""
    generate_comprehensive_admin_data()
    
    # Check if NGO is approved
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data:
        return jsonify({'success': False, 'message': 'NGO not found'})
    
    try:
        withdrawal_amount = float(request.form.get('amount', 0))
        
        if withdrawal_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid withdrawal amount'})
        
        # Calculate available balance
        ngo_transactions = [t for t in transactions_data if t.get('ngo_name') == ngo_data['name'] and t['status'] == 'Completed']
        total_earned = sum(t['total_value'] for t in ngo_transactions)
        previous_withdrawals = ngo_data.get('total_withdrawn', 0)
        available_balance = total_earned - previous_withdrawals
        
        if withdrawal_amount > available_balance:
            return jsonify({'success': False, 'message': f'Insufficient balance. Available: ₹{available_balance:,}'})
        
        # Process withdrawal
        ngo_data['total_withdrawn'] = previous_withdrawals + withdrawal_amount
        ngo_data['available_balance'] = available_balance - withdrawal_amount
        
        # Create withdrawal record
        withdrawal_record = {
            'id': f'WTH{random.randint(100000, 999999)}',
            'ngo_id': ngo_data['id'],
            'amount': withdrawal_amount,
            'withdrawal_date': datetime.now(),
            'status': 'Completed',
            'bank_details': {
                'bank_name': ngo_data.get('bank_name', ''),
                'account_number': ngo_data.get('account_number', '')
            }
        }
        
        # Store withdrawal record
        if not hasattr(app, 'ngo_withdrawals'):
            app.ngo_withdrawals = []
        app.ngo_withdrawals.append(withdrawal_record)
        
        return jsonify({
            'success': True, 
            'message': f'Withdrawal of ₹{withdrawal_amount:,} processed successfully for {ngo_data["name"]}. Funds will be transferred to your registered bank account.',
            'new_balance': available_balance - withdrawal_amount
        })
        
    except Exception as e:
        logger.error(f"Failed to process withdrawal: {e}")
        return jsonify({'success': False, 'message': 'Withdrawal failed. Please try again.'})

@ngo_bp.route("/projects")
@login_required(['ngo'])
def projects_list():
    """NGO Projects List with status filtering"""
    generate_comprehensive_admin_data()
    
    # Get current NGO
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data:
        # Use demo data for testing
        ngo_name = admin_ngos_data[0]['name'] if admin_ngos_data else 'Demo NGO'
    else:
        ngo_name = ngo_data['name']
    
    # Get all projects for this NGO
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo_name]
    
    # Filter by status if requested
    status_filter = request.args.get('status', 'all')
    if status_filter != 'all':
        if status_filter == 'verified':
            ngo_projects = [p for p in ngo_projects if p['status'] == 'Verified']
        elif status_filter == 'pending':
            ngo_projects = [p for p in ngo_projects if p['status'] in ['Pending Review', 'Under Verification', 'Documents Missing']]
        elif status_filter == 'rejected':
            ngo_projects = [p for p in ngo_projects if p['status'] == 'Rejected']
    
    # Group projects by status for dashboard display
    projects_by_status = {
        'verified': [p for p in ngo_projects if p['status'] == 'Verified'],
        'pending': [p for p in ngo_projects if p['status'] in ['Pending Review', 'Under Verification', 'Documents Missing']],
        'rejected': [p for p in ngo_projects if p['status'] == 'Rejected']
    }
    
    return render_template("ngo/projects.html", 
                         projects=ngo_projects,
                         projects_by_status=projects_by_status,
                         status_filter=status_filter,
                         ngo=ngo_data or {'name': ngo_name})

@ngo_bp.route("/projects/new", methods=['GET', 'POST'])
@login_required(['ngo'])
def ngo_projects_new():
    """New Project Registration"""
    if request.method == 'POST':
        return submit_project()
    return render_template('ngo/project_new.html', active='new_project')

@ngo_bp.route("/projects/submit", methods=['POST'])
@login_required(['ngo'])
def submit_project():
    """Handle project submission and add to admin database with enhanced file handling"""
    import os
    from werkzeug.utils import secure_filename
    from datetime import datetime
    import uuid
    import json
    
    try:
        # Generate comprehensive admin data to ensure the lists are initialized
        generate_comprehensive_admin_data()
        
        # Get current NGO (in production, this would come from session)
        user_email = session.get('user_email')
        ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
        
        if not ngo_data:
            ngo_name = admin_ngos_data[0]['name'] if admin_ngos_data else 'Demo NGO'
            ngo_id = admin_ngos_data[0]['id'] if admin_ngos_data else 'NGO2000'
        else:
            ngo_name = ngo_data['name']
            ngo_id = ngo_data['id']
        
        # Generate new project ID (ensure it doesn't conflict with existing ones)
        existing_ids = [p['id'] for p in admin_projects_data]
        project_id = None
        for i in range(1026, 9999):  # Start from PROJ1026 to avoid conflicts with demo data
            potential_id = f'PROJ{i}'
            if potential_id not in existing_ids:
                project_id = potential_id
                break
        
        if not project_id:
            project_id = f'PROJ{random.randint(5000, 9999)}'
        
        # Create project directory for file uploads
        project_upload_dir = os.path.join('uploads', 'projects', project_id)
        os.makedirs(project_upload_dir, exist_ok=True)
        os.makedirs(os.path.join(project_upload_dir, 'baseline'), exist_ok=True)
        os.makedirs(os.path.join(project_upload_dir, 'media'), exist_ok=True)
        
        # Helper function for secure file handling
        def save_uploaded_file(file, upload_path, allowed_extensions=None):
            if not file or file.filename == '':
                return None
            
            if allowed_extensions:
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if file_ext not in allowed_extensions:
                    return None
            
            # Generate unique filename to prevent conflicts
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_path, unique_filename)
            
            # Save file
            file.save(file_path)
            return {
                'original_name': file.filename,
                'saved_name': unique_filename,
                'file_path': file_path,
                'upload_date': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path)
            }
        
        # Process baseline condition upload
        baseline_file_info = None
        if 'baseline' in request.files:
            baseline_file = request.files['baseline']
            allowed_baseline_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'tiff', 'xlsx', 'xls', 'csv'}
            baseline_upload_path = os.path.join(project_upload_dir, 'baseline')
            baseline_file_info = save_uploaded_file(baseline_file, baseline_upload_path, allowed_baseline_extensions)
        
        # Process media uploads (plant images)
        uploaded_images = []
        if 'media' in request.files:
            media_files = request.files.getlist('media')
            allowed_media_extensions = {'jpg', 'jpeg', 'png', 'gif', 'tiff', 'webp'}
            media_upload_path = os.path.join(project_upload_dir, 'media')
            
            for media_file in media_files:
                if media_file and media_file.filename != '':
                    media_info = save_uploaded_file(media_file, media_upload_path, allowed_media_extensions)
                    if media_info:
                        uploaded_images.append(media_info)
        
        # Parse location coordinates from form
        location_coordinates = None
        exact_location_data = None
        location_string = request.form.get('location', '')
        
        if location_string:
            try:
                # Try to parse JSON coordinates from the form
                if location_string.startswith('{'):
                    location_data = json.loads(location_string)
                    location_coordinates = {
                        'latitude': float(location_data.get('lat', 0)),
                        'longitude': float(location_data.get('lng', 0))
                    }
                    exact_location_data = location_data
                else:
                    # Parse comma-separated coordinates
                    coords = location_string.split(',')
                    if len(coords) >= 2:
                        location_coordinates = {
                            'latitude': float(coords[0].strip()),
                            'longitude': float(coords[1].strip())
                        }
                        exact_location_data = {
                            'lat': location_coordinates['latitude'],
                            'lng': location_coordinates['longitude'],
                            'address': request.form.get('admin_area', 'Location provided')
                        }
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to parse location coordinates: {e}")
                # Keep location as string for fallback
        
        # Extract form data with enhanced structure
        project_data = {
            'id': project_id,
            'name': request.form.get('name', '').strip(),
            'ngo_name': ngo_name,
            'ngo_id': ngo_id,
            'description': request.form.get('description', ''),
            'ecosystem': request.form.get('ecosystem', 'Mangrove'),
            'start_date': request.form.get('start_date'),
            'area': float(request.form.get('area', 0)) if request.form.get('area') else 0,
            'admin_area': request.form.get('admin_area', ''),
            'species': request.form.get('species', ''),
            'number_of_trees': int(request.form.get('number_of_trees', 0)) if request.form.get('number_of_trees') else 0,
            'seedlings': int(request.form.get('seedlings', 0)) if request.form.get('seedlings') else 0,
            'carbon_credits': float(request.form.get('carbon_credits', 0)) if request.form.get('carbon_credits') else 0,
            'location': location_string,  # Keep original string for backward compatibility
            'tree_height': float(request.form.get('tree_height', 0)) if request.form.get('tree_height') else 0,
            'tree_dbh': float(request.form.get('tree_dbh', 0)) if request.form.get('tree_dbh') else 0,
            'tree_age': int(request.form.get('tree_age', 0)) if request.form.get('tree_age') else 0,
            'tree_species': request.form.get('tree_species', ''),
            'status': 'Pending Review',
            'submission_date': datetime.now(),
            'approval_date': None,
            'credits_requested': float(request.form.get('carbon_credits', 0)) if request.form.get('carbon_credits') else 0,
            'credits_approved': 0,
            'token_id': None,
            'verification_notes': '',
            'last_updated': datetime.now(),
            'contact_person': f'Contact Person for {ngo_name}',
            'phone': ngo_data['phone'] if ngo_data else admin_ngos_data[0]['phone'] if admin_ngos_data else '+91-9876543210',
            'email': ngo_data['email'] if ngo_data else admin_ngos_data[0]['email'] if admin_ngos_data else 'contact@ngo.org',
            'documents': ['Project Proposal', 'Environmental Assessment'],
            # New fields for location parsing
            'state': 'Maharashtra',  # Default, could be extracted from location
            'district': request.form.get('admin_area', '').split(',')[0] if request.form.get('admin_area') else 'Mumbai',
            
            # NEW ENHANCED FIELDS FOR REAL-TIME ADMIN VISIBILITY
            'location_coordinates': location_coordinates,
            'exact_location_data': exact_location_data,
            'baseline_file': baseline_file_info,
            'uploaded_images': uploaded_images,
            'upload_directory': project_upload_dir,
            'total_uploaded_files': len(uploaded_images) + (1 if baseline_file_info else 0),
            'submission_timestamp': datetime.now().isoformat(),
            'real_time_data': {
                'files_uploaded': bool(baseline_file_info or uploaded_images),
                'coordinates_provided': bool(location_coordinates),
                'baseline_provided': bool(baseline_file_info),
                'images_count': len(uploaded_images)
            }
        }
        
        # Validate required fields
        if not project_data['name']:
            flash('Project name is required', 'error')
            return redirect(url_for('ngo.ngo_projects_new'))
        
        if project_data['number_of_trees'] <= 0:
            flash('Number of trees must be greater than 0', 'error')
            return redirect(url_for('ngo.ngo_projects_new'))
        
        if project_data['carbon_credits'] <= 0:
            flash('Please calculate carbon credits before submitting', 'error')
            return redirect(url_for('ngo.ngo_projects_new'))
        
        # Add to admin projects database
        admin_projects_data.append(project_data)
        
        # Enhanced logging for real-time monitoring with file and location info
        logger.info(f"NEW PROJECT CREATED: {project_id} - {project_data['name']} by {ngo_name} - Status: {project_data['status']}")
        logger.info(f"PROJECT FILES: Baseline: {bool(baseline_file_info)}, Images: {len(uploaded_images)}, Coordinates: {bool(location_coordinates)}")
        logger.info(f"PROJECT LOCATION: {location_coordinates if location_coordinates else 'No coordinates provided'}")
        logger.info(f"Total projects in system: {len(admin_projects_data)}")
        
        # Submit to blockchain for immutable record
        try:
            blockchain_hash = blockchain_mrv.submit_project_to_blockchain(project_data)
            project_data['blockchain_hash'] = blockchain_hash
            logger.info(f"Project {project_id} submitted to blockchain: {blockchain_hash}")
        except Exception as e:
            logger.warning(f'Blockchain recording failed for project {project_id}: {str(e)}')
        
        # Create MRV workflow for automated verification
        try:
            import asyncio
            workflow = asyncio.run(mrv_workflow_engine.create_workflow(project_data))
            project_data['workflow_id'] = workflow.workflow_id
            
            # Create enhanced success message with file upload info
            success_message = f'Project "{project_data["name"]}" submitted successfully!\n'
            success_message += f'Project ID: {project_id}\n'
            success_message += f'MRV Workflow ID: {workflow.workflow_id}\n'
            success_message += f'Verification Score: {workflow.verification_score:.1%}\n'
            
            # Add file upload status
            if baseline_file_info:
                success_message += f'✓ Baseline condition file uploaded: {baseline_file_info["original_name"]}\n'
            if uploaded_images:
                success_message += f'✓ {len(uploaded_images)} plant image(s) uploaded\n'
            if location_coordinates:
                success_message += f'✓ GPS coordinates recorded: {location_coordinates["latitude"]:.4f}, {location_coordinates["longitude"]:.4f}\n'
            
            success_message += '\nProject is now visible in admin portal for real-time review!'
            flash(success_message, 'success')
                  
            logger.info(f"Created MRV workflow {workflow.workflow_id} for project {project_id}")
        except Exception as e:
            logger.error(f'MRV workflow creation failed for project {project_id}: {str(e)}')
            flash(f'Project submitted but automated verification setup failed: {str(e)}', 'warning')
        
        return redirect(url_for('ngo.dashboard_view'))
        
    except Exception as e:
        flash(f'Error submitting project: {str(e)}', 'error')
        return redirect(url_for('ngo.ngo_projects_new'))

@ngo_bp.route("/projects/<project_id>")
@login_required(['ngo'])
def ngo_project_details(project_id):
    """NGO Project Details Page"""
    generate_comprehensive_admin_data()
    
    # Check if NGO is approved
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data or ngo_data['status'] != 'Verified':
        flash('Access denied. Your NGO registration is pending admin approval.', 'warning')
        logout_user()
        return redirect(url_for('ngo.ngo_login'))
    
    # Find the specific project
    project = next((p for p in admin_projects_data if p['id'] == project_id and p['ngo_name'] == ngo_data['name']), None)
    
    if not project:
        flash('Project not found or access denied', 'error')
        return redirect(url_for('ngo.ngo_projects'))
    
    return render_template('ngo/project_details.html', project=project, ngo=ngo_data, active='projects')

@ngo_bp.route("/projects/<project_id>/resubmit", methods=['POST'])
@login_required(['ngo'])
def resubmit_project(project_id):
    """Resubmit project after admin feedback"""
    generate_comprehensive_admin_data()
    
    # Check if NGO is approved
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data or ngo_data['status'] != 'Verified':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Find the specific project
    project = next((p for p in admin_projects_data if p['id'] == project_id and p['ngo_name'] == ngo_data['name']), None)
    
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'})
    
    if project['status'] not in ['Needs Revision', 'Rejected']:
        return jsonify({'success': False, 'message': 'Project cannot be resubmitted in current status'})
    
    try:
        # Update project with resubmission data
        project['status'] = 'Under Verification'
        project['resubmission_date'] = datetime.now()
        project['resubmission_notes'] = request.form.get('resubmission_notes', '')
        project['revision_count'] = project.get('revision_count', 0) + 1
        
        # Update specific fields if provided
        if request.form.get('updated_description'):
            project['description'] = request.form.get('updated_description')
        
        if request.form.get('updated_methodology'):
            project['methodology'] = request.form.get('updated_methodology')
        
        if request.form.get('updated_timeline'):
            project['timeline'] = request.form.get('updated_timeline')
        
        if request.form.get('updated_area'):
            try:
                project['area'] = float(request.form.get('updated_area'))
            except (ValueError, TypeError):
                pass
        
        if request.form.get('updated_credits_requested'):
            try:
                project['credits_requested'] = int(request.form.get('updated_credits_requested'))
            except (ValueError, TypeError):
                pass
        
        if request.form.get('updated_location'):
            project['location'] = request.form.get('updated_location')
        
        if request.form.get('updated_ecosystem'):
            project['ecosystem'] = request.form.get('updated_ecosystem')
        
        # Clear previous rejection feedback
        project['admin_feedback'] = f"Project resubmitted (Revision #{project['revision_count']}): {project['resubmission_notes']}"
        
        return jsonify({
            'success': True,
            'message': f'Project "{project["name"]}" has been resubmitted for review. Admin will review the changes shortly.',
            'project_status': project['status']
        })
        
    except Exception as e:
        logger.error(f"Failed to resubmit project: {e}")
        return jsonify({'success': False, 'message': 'Resubmission failed. Please try again.'})

@ngo_bp.route("/mobile-data-collection")
@login_required(['ngo'])
def mobile_data_collection():
    """Mobile Field Data Collection Interface"""
    generate_comprehensive_admin_data()
    
    # Check if NGO is approved
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data or ngo_data['status'] != 'Verified':
        flash('Access denied. Your NGO registration is pending admin approval.', 'warning')
        logout_user()
        return redirect(url_for('ngo.ngo_login'))
    
    return render_template('ngo/mobile_data_collection.html', active='mobile_collection')

@ngo_bp.route("/satellite-monitoring/<project_id>")
@login_required(['ngo'])
def satellite_analysis(project_id):
    """Satellite Analysis Page with Charts for specific project"""
    generate_comprehensive_admin_data()
    
    # Check if NGO is approved
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data or ngo_data['status'] != 'Verified':
        flash('Access denied. Your NGO registration is pending admin approval.', 'warning')
        logout_user()
        return redirect(url_for('ngo.ngo_login'))
    
    # Find the specific project
    project = next((p for p in admin_projects_data if p['id'] == project_id and p['ngo_name'] == ngo_data['name']), None)
    
    if not project:
        flash('Project not found or access denied', 'error')
        return redirect(url_for('ngo.satellite_monitoring'))
    
    return render_template('ngo/satellite_analysis.html', project=project, ngo=ngo_data, active='satellite')

@ngo_bp.route("/field-data/submit", methods=['POST'])
@login_required(['ngo'])
def submit_field_data():
    """Handle mobile field data submission"""
    try:
        data = request.get_json()
        
        # Get current NGO
        user_email = session.get('user_email')
        ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
        
        if not ngo_data:
            return jsonify({'success': False, 'message': 'NGO not found'}), 404
        
        # Generate field data record ID
        field_data_id = f'FD{random.randint(100000, 999999)}'
        
        # Create field data record
        field_record = {
            'id': field_data_id,
            'ngo_id': ngo_data['id'],
            'ngo_name': ngo_data['name'],
            'project_id': data.get('project_id'),
            'collection_date': data.get('collection_date'),
            'location': data.get('location', {}),
            'ecosystem_data': {
                'type': data.get('ecosystem_type'),
                'area_covered': float(data.get('area_covered', 0)),
                'tree_count': int(data.get('tree_count', 0)),
                'avg_height': float(data.get('avg_height', 0)),
                'avg_diameter': float(data.get('avg_diameter', 0)),
                'species_identified': data.get('species_identified', '')
            },
            'environmental_conditions': {
                'temperature': float(data.get('temperature', 0)) if data.get('temperature') else None,
                'humidity': int(data.get('humidity', 0)) if data.get('humidity') else None,
                'water_salinity': float(data.get('water_salinity', 0)) if data.get('water_salinity') else None,
                'soil_ph': float(data.get('soil_ph', 0)) if data.get('soil_ph') else None,
                'weather_conditions': data.get('weather_conditions', '')
            },
            'field_observations': {
                'restoration_progress': data.get('restoration_progress', ''),
                'wildlife_observed': data.get('wildlife_observed', ''),
                'challenges': data.get('challenges', ''),
                'additional_notes': data.get('additional_notes', '')
            },
            'photos': data.get('photos', []),
            'submission_timestamp': datetime.now(),
            'status': 'Submitted',
            'blockchain_hash': None
        }
        
        # Submit to blockchain for immutable storage
        try:
            blockchain_hash = blockchain_mrv.record_field_data(field_record)
            field_record['blockchain_hash'] = blockchain_hash
        except Exception as e:
            logger.warning(f"Blockchain recording failed for field data {field_data_id}: {e}")
        
        # Store field data (in production, save to database)
        if not hasattr(app, 'field_data_records'):
            app.field_data_records = []
        app.field_data_records.append(field_record)
        
        # Update project with field data reference
        project = next((p for p in admin_projects_data if p['id'] == data.get('project_id')), None)
        if project:
            if 'field_data_records' not in project:
                project['field_data_records'] = []
            project['field_data_records'].append(field_data_id)
        
        logger.info(f"Field data submitted: {field_data_id} for project {data.get('project_id')}")
        
        return jsonify({
            'success': True,
            'message': 'Field data submitted successfully',
            'field_data_id': field_data_id,
            'blockchain_hash': blockchain_hash
        })
        
    except Exception as e:
        logger.error(f"Failed to submit field data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@ngo_bp.route("/credits")
@login_required(['ngo'])
def credits_view():
    """NGO Credits View with real data from verified projects"""
    generate_comprehensive_admin_data()
    
    # Get current NGO
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data:
        # Use first NGO for demo purposes
        ngo_data = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO', 'email': 'demo@ngo.com'}
    
    # Get all projects for this NGO
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo_data['name']]
    
    # Generate credits data from verified projects
    credits_data = []
    for project in ngo_projects:
        if project['status'] == 'Verified' and project.get('credits_approved', 0) > 0:
            # Check if credits were sold (simulate with random for now)
            is_sold = random.random() < 0.3  # 30% chance of being sold
            price_per_credit = random.randint(180, 280)
            revenue = project['credits_approved'] * price_per_credit if is_sold else 0
            
            credits_data.append({
                'project': project['name'],
                'vintage': project['approval_date'].year if project['approval_date'] else 2024,
                'amount': project['credits_approved'],
                'verification': 'Verified',
                'token': project.get('token_id', f"BC{random.randint(100000, 999999)}"),
                'status': 'Sold' if is_sold else 'Available',
                'revenue': revenue,
                'project_id': project['id'],
                'blockchain_verified': bool(project.get('token_id'))
            })
    
    # Add pending credits from projects under verification
    for project in ngo_projects:
        if project['status'] in ['Under Verification', 'Documents Missing'] and project.get('credits_requested', 0) > 0:
            credits_data.append({
                'project': project['name'],
                'vintage': 2024,
                'amount': project['credits_requested'],
                'verification': 'Pending',
                'token': 'Pending Verification',
                'status': 'Pending',
                'revenue': 0,
                'project_id': project['id'],
                'blockchain_verified': False
            })
    
    # Calculate stats from real data
    total_credits = sum(c['amount'] for c in credits_data if c['verification'] == 'Verified')
    verified_credits = sum(c['amount'] for c in credits_data if c['verification'] == 'Verified')
    pending_credits = sum(c['amount'] for c in credits_data if c['verification'] == 'Pending')
    sold_credits = sum(c['amount'] for c in credits_data if c['status'] == 'Sold')
    total_revenue = sum(c['revenue'] for c in credits_data if c['status'] == 'Sold')
    
    stats = {
        'total_credits': total_credits,
        'verified_credits': verified_credits,
        'pending_credits': pending_credits,
        'sold_credits': sold_credits,
        'total_revenue': total_revenue,
        'ngo_name': ngo_data['name'],
        'total_projects': len([p for p in ngo_projects if p['status'] == 'Verified'])
    }
    
    return render_template("ngo/credits.html", credits=credits_data, stats=stats, ngo=ngo_data)


@ngo_bp.route("/upload/tree_data", methods=['POST'])
@login_required(['ngo'])
def process_tree_data():
    """Process uploaded CSV/Excel file with tree data and extract statistics"""
    if 'tree_data_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['tree_data_file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    try:
        # Determine file type and read accordingly
        filename = file.filename.lower()
        
        if filename.endswith('.csv'):
            # Read CSV file
            df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            # Read Excel file
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'error': 'Unsupported file format. Please use CSV or Excel files.'})
        
        # Standardize column names (case insensitive)
        df.columns = df.columns.str.lower().str.strip()
        
        # Map common column variations to standard names
        column_mappings = {
            'height': ['height', 'tree_height', 'h', 'ht', 'height_m', 'height_cm'],
            'dbh': ['dbh', 'diameter', 'trunk_diameter', 'd', 'diameter_cm', 'diameter_m', 'breast_height_diameter'],
            'age': ['age', 'tree_age', 'years', 'age_years'],
            'species': ['species', 'tree_species', 'type', 'tree_type']
        }
        
        # Find the actual column names in the dataframe
        actual_columns = {}
        for standard_name, variations in column_mappings.items():
            for variation in variations:
                if variation in df.columns:
                    actual_columns[standard_name] = variation
                    break
        
        # Check if we have the minimum required columns
        if 'height' not in actual_columns and 'dbh' not in actual_columns:
            return jsonify({
                'success': False, 
                'error': 'File must contain at least height or DBH columns. Supported column names: height, dbh, diameter, age, species'
            })
        
        # Process the data
        total_trees = len(df)
        
        if total_trees == 0:
            return jsonify({'success': False, 'error': 'No data found in the file'})
        
        # Initialize statistics
        stats = {
            'total_trees': total_trees,
            'avg_height': None,
            'avg_dbh': None,
            'avg_age': None,
            'species_list': [],
            'data_quality': {}
        }
        
        # Process height data
        if 'height' in actual_columns:
            height_col = actual_columns['height']
            height_data = pd.to_numeric(df[height_col], errors='coerce').dropna()
            
            if len(height_data) > 0:
                avg_height = height_data.mean()
                
                # Convert from cm to meters if values seem to be in cm (> 50)
                if avg_height > 50:
                    avg_height = avg_height / 100
                    stats['data_quality']['height_converted_cm_to_m'] = True
                
                stats['avg_height'] = round(avg_height, 2)
                stats['data_quality']['height_records'] = len(height_data)
        
        # Process DBH data
        if 'dbh' in actual_columns:
            dbh_col = actual_columns['dbh']
            dbh_data = pd.to_numeric(df[dbh_col], errors='coerce').dropna()
            
            if len(dbh_data) > 0:
                avg_dbh = dbh_data.mean()
                
                # Convert from cm to meters if values seem to be in cm (> 2)
                if avg_dbh > 2:
                    avg_dbh = avg_dbh / 100
                    stats['data_quality']['dbh_converted_cm_to_m'] = True
                
                stats['avg_dbh'] = round(avg_dbh, 3)
                stats['data_quality']['dbh_records'] = len(dbh_data)
        
        # Process age data
        if 'age' in actual_columns:
            age_col = actual_columns['age']
            age_data = pd.to_numeric(df[age_col], errors='coerce').dropna()
            
            if len(age_data) > 0:
                stats['avg_age'] = round(age_data.mean(), 1)
                stats['data_quality']['age_records'] = len(age_data)
        
        # Process species data
        if 'species' in actual_columns:
            species_col = actual_columns['species']
            species_data = df[species_col].dropna().unique()
            stats['species_list'] = [str(species).strip() for species in species_data if str(species).strip()]
        
        # Validate that we have meaningful data
        if stats['avg_height'] is None and stats['avg_dbh'] is None:
            return jsonify({
                'success': False, 
                'error': 'No valid numeric data found for height or DBH columns'
            })
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {total_trees} tree records',
            'statistics': stats,
            'columns_found': actual_columns
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        })

@ngo_bp.route("/upload/analyze", methods=['POST'])
@login_required(['ngo'])
def analyze_image():
    """AI Image Analysis for tree species and carbon estimation with plant validation"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'})
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({'success': False, 'error': 'No image selected'})
    
    try:
        # Read image data and convert to base64 for plant detection
        image_data = image.read()
        image.seek(0)  # Reset file pointer
        
        # Convert to base64 for plant detection
        import base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # Validate if the image contains plants/trees
        is_plant, validation_result = detect_plant_in_image(encoded_image)
        
        if not is_plant:
            return jsonify({
                'success': False,
                'error': 'Invalid image: Only plant/tree images are accepted for carbon credit analysis.',
                'validation_details': validation_result if isinstance(validation_result, dict) else {'message': validation_result}
            })
        
        # Enhanced AI analysis with plant validation results
        confidence_score = validation_result['confidence'] if isinstance(validation_result, dict) else 80.0
        
        # Select species based on plant characteristics detected
        if validation_result.get('plant_percentage', 0) > 25:
            # High plant content - dense vegetation
            tree_species = random.choice(['Rhizophora', 'Avicennia', 'Mangrove Forest', 'Dense Coastal Vegetation'])
        elif validation_result.get('plant_percentage', 0) > 15:
            # Moderate plant content - individual trees
            tree_species = random.choice(['Coastal Tree', 'Mangrove Sapling', 'Marine Pine', 'Neem', 'Banyan'])
        else:
            # Lower plant content but still valid
            tree_species = random.choice(['Young Sapling', 'Coastal Vegetation', 'Small Tree'])
        
        # Calculate credits based on detected plant content and measurements
        base_credits = random.uniform(0.5, 5.0)  # tCO2e per tree
        plant_multiplier = min(validation_result.get('plant_percentage', 15) / 20, 2.5)  # Scale based on plant density
        estimated_credits = base_credits * plant_multiplier
        
        # Check if tree measurements were provided for scientific calculation
        height = request.form.get('height')
        dbh = request.form.get('dbh')
        calculation_method = 'image_estimation_with_cv'
        
        if height and dbh:
            # Use scientific calculation with provided measurements
            height_val = float(height)
            dbh_val = float(dbh)
            # Basic allometric formula: AGB = 0.0673 * (DBH^2 * H)^0.976
            above_ground_biomass = 0.0673 * ((dbh_val * 100) ** 2 * height_val) ** 0.976  # kg
            carbon_content = above_ground_biomass * 0.47  # 47% carbon content
            estimated_credits = (carbon_content / 1000) * 3.67  # Convert to CO2 tonnes
            calculation_method = 'scientific_allometric'
        
        # Mock GPS extraction (would extract from EXIF in production)
        mock_location = {
            'latitude': random.uniform(8.0, 37.0),  # India latitude range
            'longitude': random.uniform(68.0, 97.0)  # India longitude range
        }
        
        analysis_result = {
            'success': True,
            'analysis': {
                'species': tree_species,
                'estimated_carbon_credits': round(estimated_credits, 3),
                'calculation_method': calculation_method,
                'confidence': round(confidence_score / 100, 2),  # Convert to 0-1 scale
                'location': mock_location,
                'tree_count': random.randint(1, max(1, int(validation_result.get('plant_percentage', 15) / 12))),
                'health_status': 'Healthy',
                'plant_coverage': f"{validation_result.get('plant_percentage', 0):.1f}%",
                'validation': {
                    'plant_detected': True,
                    'confidence': confidence_score,
                    'analysis_method': 'Computer Vision + Color Analysis'
                }
            }
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Image analysis error: {str(e)}'
        })

@ngo_bp.route("/uploads/<project_id>/<file_type>/<filename>")
@login_required(['ngo', 'admin', 'verifier'])
def serve_project_file(project_id, file_type, filename):
    """Secure file serving for project uploads with access control"""
    import os
    from flask import send_file, abort
    
    try:
        # Validate file type
        if file_type not in ['baseline', 'media']:
            abort(404)
        
        # Check if user has access to this project
        user_role = session.get('user_role')
        user_email = session.get('user_email')
        
        # Find the project
        generate_comprehensive_admin_data()
        project = next((p for p in admin_projects_data if p['id'] == project_id), None)
        
        if not project:
            abort(404)
        
        # Access control: NGOs can only see their own projects, admins/verifiers can see all
        if user_role == 'ngo':
            ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
            if not ngo_data or project['ngo_name'] != ngo_data['name']:
                abort(403)
        
        # Construct file path
        file_path = os.path.join('uploads', 'projects', project_id, file_type, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            abort(404)
        
        # Serve the file
        return send_file(file_path)
        
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        abort(500)

@ngo_bp.route("/calculate/tree_carbon", methods=['POST'])
def calculate_tree_carbon():
    """Scientific carbon sequestration calculation using allometric equations"""
    data = request.get_json()
    
    try:
        height = data['height']  # meters
        dbh = data['dbh']  # meters 
        latitude = data.get('latitude', 20.5937)
        longitude = data.get('longitude', 78.9629)
        species = data.get('species')
        age = data.get('age')
        number_of_trees = data.get('number_of_trees', 1)
        
        # Convert DBH to cm for calculation
        dbh_cm = dbh * 100
        
        # Climate adjustment factor based on location (mock)
        climate_factor = 1.0 + (abs(latitude - 23.5) / 100)  # Tropic of Cancer adjustment
        
        # Allometric equation: AGB = 0.0673 * (DBH^2 * H)^0.976 (Chave et al., 2014)
        above_ground_biomass = 0.0673 * ((dbh_cm ** 2) * height) ** 0.976  # kg
        
        # Below ground biomass (typically 20-25% of AGB for trees)
        below_ground_biomass = above_ground_biomass * 0.22
        total_biomass = above_ground_biomass + below_ground_biomass
        
        # Carbon content (47% of dry biomass)
        carbon_content = total_biomass * 0.47
        
        # CO2 sequestration (carbon * 3.67)
        co2_sequestered = carbon_content * 3.67 / 1000  # tonnes
        
        # Apply climate factor
        co2_adjusted = co2_sequestered * climate_factor
        
        # Multiply by number of trees for total project sequestration
        total_co2_sequestered = co2_adjusted * number_of_trees
        total_biomass = total_biomass * number_of_trees
        total_carbon_content = carbon_content * number_of_trees
        
        # Annual sequestration (assuming 20-year growth)
        annual_co2 = total_co2_sequestered / (age if age else 20)
        
        # Environmental impact calculations
        car_emissions_offset = total_co2_sequestered * 365 / 4.6  # Average car emits 4.6 tonnes CO2/year
        economic_value = total_co2_sequestered * 25  # $25 per tonne CO2 (carbon price)
        
        calculation_result = {
            'success': True,
            'calculation': {
                'project_details': {
                    'number_of_trees': number_of_trees,
                    'per_tree_co2_sequestration': round(co2_adjusted, 6),
                    'total_project_co2_sequestration': round(total_co2_sequestered, 6)
                },
                'biomass_analysis': {
                    'per_tree_above_ground_biomass_kg': round(above_ground_biomass, 2),
                    'per_tree_below_ground_biomass_kg': round(below_ground_biomass, 2),
                    'total_project_biomass_kg': round(total_biomass, 2),
                    'total_project_carbon_content_kg': round(total_carbon_content, 2)
                },
                'carbon_sequestration': {
                    'total_co2_sequestered_tonnes': round(total_co2_sequestered, 6),
                    'annual_co2_sequestration_tonnes': round(annual_co2, 6),
                    'climate_adjustment_factor': round(climate_factor, 2)
                },
                'environmental_impact': {
                    'equivalent_car_emissions_offset_days': round(car_emissions_offset, 1),
                    'economic_value_usd': round(economic_value, 2)
                },
                'methodology': 'Chave et al. (2014) allometric equations',
                'species': species,
                'location': {'latitude': latitude, 'longitude': longitude}
            }
        }
        
        return jsonify(calculation_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Calculation error: {str(e)}'
        })

def detect_plant_in_image(image_data):
    """Detect if the image contains plants/trees using computer vision"""
    try:
        # Remove the data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return False, "Unable to decode image"
        
        # Convert BGR to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define range for green colors (plants/leaves)
        # Lower and upper bounds for green in HSV
        lower_green1 = np.array([35, 40, 40])   # Light green
        upper_green1 = np.array([85, 255, 255]) # Dark green
        
        # Create mask for green colors
        green_mask = cv2.inRange(hsv, lower_green1, upper_green1)
        
        # Define range for brown colors (tree trunks/branches)
        lower_brown = np.array([10, 50, 20])    # Brown tones
        upper_brown = np.array([20, 255, 200])
        
        # Create mask for brown colors
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
        
        # Combine green and brown masks
        plant_mask = cv2.bitwise_or(green_mask, brown_mask)
        
        # Calculate the percentage of plant-colored pixels
        total_pixels = image.shape[0] * image.shape[1]
        plant_pixels = cv2.countNonZero(plant_mask)
        plant_percentage = (plant_pixels / total_pixels) * 100
        
        # Additional texture analysis for leaves/branches
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur and detect edges
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Count edge pixels (indicates organic shapes)
        edge_pixels = cv2.countNonZero(edges)
        edge_percentage = (edge_pixels / total_pixels) * 100
        
        # Check if image likely contains plants based on:
        # 1. Green/brown color content (at least 15%)
        # 2. Edge content indicating organic shapes (at least 8%)
        # 3. Combined score threshold
        
        is_plant = False
        confidence = 0.0
        reasons = []
        
        if plant_percentage >= 15.0:
            is_plant = True
            reasons.append(f"Plant colors: {plant_percentage:.1f}%")
            confidence += plant_percentage * 0.6
        
        if edge_percentage >= 8.0:
            reasons.append(f"Organic shapes: {edge_percentage:.1f}%")
            confidence += edge_percentage * 0.4
        
        # Final validation - need both color and shape indicators
        if plant_percentage >= 10.0 and edge_percentage >= 5.0:
            is_plant = True
            confidence = min(confidence, 95.0)  # Cap at 95%
        else:
            is_plant = False
            confidence = 0.0
            reasons = ["Insufficient plant characteristics detected"]
        
        return is_plant, {
            'confidence': round(confidence, 1),
            'plant_percentage': round(plant_percentage, 1),
            'edge_percentage': round(edge_percentage, 1),
            'reasons': reasons
        }
        
    except Exception as e:
        return False, f"Image analysis error: {str(e)}"

@ngo_bp.route("/camera/capture", methods=['POST'])
def capture_photo():
    """Handle camera photo capture and analysis with plant validation"""
    data = request.get_json()
    
    if not data.get('image_data'):
        return jsonify({'success': False, 'error': 'No image data provided'})
    
    try:
        # First, validate if the image contains plants/trees
        is_plant, validation_result = detect_plant_in_image(data['image_data'])
        
        if not is_plant:
            return jsonify({
                'success': False,
                'error': 'Invalid image: Only plant/tree images are accepted for carbon credit analysis.',
                'validation_details': validation_result if isinstance(validation_result, dict) else {'message': validation_result}
            })
        
        # Save the captured image (mock filename)
        filename = f'capture_{uuid.uuid4().hex[:8]}.jpg'
        
        # Enhanced AI analysis of captured plant photo
        # Use validation confidence to influence species detection
        confidence_score = validation_result['confidence'] if isinstance(validation_result, dict) else 80.0
        
        # Select species based on plant characteristics detected
        if validation_result.get('plant_percentage', 0) > 25:
            # High plant content - likely dense vegetation
            species = random.choice(['Rhizophora', 'Avicennia', 'Mangrove Forest'])
        elif validation_result.get('plant_percentage', 0) > 15:
            # Moderate plant content - individual trees
            species = random.choice(['Coastal Tree', 'Mangrove Sapling', 'Marine Pine'])
        else:
            # Lower plant content but still valid
            species = random.choice(['Young Sapling', 'Coastal Vegetation'])
        
        # Calculate credits based on detected plant content
        base_credits = random.uniform(0.8, 3.5)
        plant_multiplier = min(validation_result.get('plant_percentage', 15) / 20, 2.0)  # Scale based on plant density
        credits = base_credits * plant_multiplier
        
        location_data = None
        if data.get('latitude') and data.get('longitude'):
            location_data = {
                'latitude': data['latitude'],
                'longitude': data['longitude']
            }
        
        analysis_result = {
            'success': True,
            'filename': filename,
            'analysis': {
                'species': species,
                'estimated_carbon_credits': round(credits, 3),
                'captured_location': location_data,
                'confidence': round(confidence_score / 100, 2),  # Convert to 0-1 scale
                'tree_count': random.randint(1, max(1, int(validation_result.get('plant_percentage', 15) / 10))),
                'health_status': 'Healthy',
                'plant_coverage': f"{validation_result.get('plant_percentage', 0):.1f}%",
                'validation': {
                    'plant_detected': True,
                    'confidence': confidence_score,
                    'analysis_method': 'Computer Vision + Color Analysis'
                }
            }
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Capture processing error: {str(e)}'
        })

@ngo_bp.route("/credits/realtime")
@login_required(['ngo'])
def credits_realtime():
    """Real-time credits data for live updates"""
    generate_comprehensive_admin_data()
    
    # Get current NGO
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data:
        # Use first NGO for demo purposes
        ngo_data = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO', 'email': 'demo@ngo.com'}
    
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo_data['name']]
    
    # Generate real-time credits data from actual projects
    credits_data = []
    for project in ngo_projects:
        if project['status'] == 'Verified' and project.get('credits_approved', 0) > 0:
            # Check if credits were sold (simulate with consistent random)
            project_hash = hash(project['id']) % 100
            is_sold = project_hash < 30  # 30% chance based on project ID
            price_per_credit = 200 + (project_hash % 80)  # Price between 200-280
            revenue = project['credits_approved'] * price_per_credit if is_sold else 0
            
            credits_data.append({
                'project': project['name'],
                'vintage': project['approval_date'].year if project['approval_date'] else 2024,
                'amount': project['credits_approved'],
                'verification': 'Verified',
                'token': project.get('token_id', f"BC{project_hash:06d}"),
                'status': 'Sold' if is_sold else 'Available',
                'revenue': revenue,
                'blockchain_verified': bool(project.get('token_id'))
            })
    
    # Add pending credits
    for project in ngo_projects:
        if project['status'] in ['Under Verification', 'Documents Missing'] and project.get('credits_requested', 0) > 0:
            credits_data.append({
                'project': project['name'],
                'vintage': 2024,
                'amount': project['credits_requested'],
                'verification': 'Pending',
                'token': 'Pending Verification',
                'status': 'Pending',
                'revenue': 0,
                'blockchain_verified': False
            })
    
    total_credits = sum(c['amount'] for c in credits_data if c['verification'] == 'Verified')
    
    return jsonify({
        'success': True,
        'total_credits': total_credits,
        'latest_credits': credits_data,
        'ngo_name': ngo_data['name'],
        'blockchain_connected': True  # Simulate blockchain connection
    })

@ngo_bp.route("/revenue/realtime")
def revenue_realtime():
    """Real-time revenue data for live updates"""
    generate_comprehensive_admin_data()
    
    # Get current NGO
    user_email = session.get('user_email')
    ngo_data = next((ngo for ngo in admin_ngos_data if ngo['email'] == user_email), None)
    
    if not ngo_data:
        # Use first NGO for demo
        ngo_data = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO', 'total_revenue': 0}
    
    # Get actual revenue from NGO data (updated by credit purchases)
    total_revenue = ngo_data.get('total_revenue', 0)
    credits_sold = ngo_data.get('credits_sold', 0)
    
    # Get transactions for this NGO
    ngo_transactions = [t for t in transactions_data if t.get('ngo_name') == ngo_data['name'] and t['type'] == 'Credit Sale']
    
    # Recent transactions (last 5)
    recent_transactions = []
    for t in sorted(ngo_transactions, key=lambda x: x['sale_date'], reverse=True)[:5]:
        recent_transactions.append({
            'transaction_id': t['transaction_id'],
            'project': t['project_name'],
            'industry_buyer': t['industry_name'],
            'credits_sold': t['credits_sold'],
            'total_value': t['total_value'],
            'sale_date': t['sale_date'].strftime('%Y-%m-%d %H:%M'),
            'status': t['status']
        })
    
    # Calculate statistics
    stats = {
        'total_revenue': total_revenue,
        'credits_sold': credits_sold,
        'total_transactions': len(ngo_transactions),
        'average_revenue_per_credit': total_revenue / max(credits_sold, 1),
        'last_sale_date': ngo_data.get('last_sale_date').strftime('%Y-%m-%d') if ngo_data.get('last_sale_date') else None
    }
    
    return jsonify({
        'success': True,
        'stats': stats,
        'recent_transactions': recent_transactions,
        'ngo_name': ngo_data['name'],
        'last_updated': datetime.now().strftime('%H:%M:%S')
    })

@ngo_bp.route("/revenue/request_payout", methods=['POST'])
def request_payout():
    """Handle payout requests"""
    amount = request.form.get('amount')
    payment_method = request.form.get('payment_method', 'bank')
    
    if not amount or float(amount) <= 0:
        return jsonify({'success': False, 'message': 'Invalid payout amount'})
    
    # Mock payout processing
    payout_id = f'PO{random.randint(100000, 999999)}'
    
    return jsonify({
        'success': True,
        'message': f'Payout request of ₹{amount} submitted successfully. Reference ID: {payout_id}',
        'payout_id': payout_id,
        'status': 'Processing',
        'estimated_completion': '2-3 business days'
    })

@ngo_bp.route("/credits/export")
def export_credits():
    """Export credits data to CSV"""
    generate_comprehensive_admin_data()
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV headers
    writer.writerow(['Project', 'Vintage', 'Credits (tCO2e)', 'Verification', 'Token ID', 'Status', 'Revenue (₹)'])
    
    # Export verified projects as credits
    for project in ngo_projects:
        if project['status'] == 'Verified':
            revenue = project['credits_approved'] * random.randint(180, 250)
            writer.writerow([
                project['name'],
                project['approval_date'].year if project['approval_date'] else 2024,
                project['credits_approved'],
                'Verified',
                project['token_id'],
                random.choice(['Available', 'Sold']),
                revenue
            ])
    
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=ngo_credits_export_{datetime.now().strftime("%Y%m%d")}.csv'
    return response

# NGO-only Satellite and Drone Monitoring Routes
@ngo_bp.route("/satellite-monitoring")
@login_required(['ngo'])
def ngo_satellite_monitoring():
    """NGO Satellite Monitoring Dashboard - NGO can only see their own projects"""
    generate_comprehensive_admin_data()
    
    # Get current NGO (in production, this would come from session)
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    
    # Get only verified projects for this NGO
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name'] and p['status'] == 'Verified']
    
    return render_template('ngo/satellite_monitoring.html', projects=ngo_projects, ngo=ngo)

@ngo_bp.route("/satellite-monitoring/<project_id>")
@login_required(['ngo'])
def ngo_satellite_project_detail(project_id):
    """NGO Detailed satellite monitoring view for a specific project"""
    generate_comprehensive_admin_data()
    
    # Get current NGO
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    
    # Find project and ensure it belongs to this NGO
    project = next((p for p in admin_projects_data if p['id'] == project_id and p['ngo_name'] == ngo['name']), None)
    if not project:
        flash('Project not found or access denied', 'error')
        return redirect(url_for('ngo.ngo_satellite_monitoring'))
    
    # Get satellite monitoring data
    try:
        satellite_data = satellite_processor.monitor_restoration_site(project)
        
        # Get IoT sensor data if available
        if project.get('location'):
            coords = satellite_processor._extract_coordinates(project['location'])
            sensor_data = sensor_network.get_sensor_readings(project_id, coords)
        else:
            sensor_data = None
        
        return render_template('ngo/satellite_project_detail.html', 
                             project=project, 
                             satellite_data=satellite_data, 
                             sensor_data=sensor_data,
                             ngo=ngo)
        
    except Exception as e:
        flash(f'Error loading satellite data: {str(e)}', 'error')
        return redirect(url_for('ngo.ngo_satellite_monitoring'))

@ngo_bp.route("/drone-monitoring")
@login_required(['ngo'])
def ngo_drone_monitoring():
    """NGO Drone Monitoring Dashboard - NGO can only see their own projects"""
    generate_comprehensive_admin_data()
    
    # Get current NGO
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    
    # Get only verified projects for this NGO
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name'] and p['status'] == 'Verified']
    
    return render_template('ngo/drone_monitoring.html', projects=ngo_projects, ngo=ngo)

@ngo_bp.route("/drone-monitoring/<project_id>")
@login_required(['ngo'])
def ngo_drone_project_detail(project_id):
    """NGO Detailed drone analysis view for a specific project"""
    generate_comprehensive_admin_data()
    
    # Get current NGO
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    
    # Find project and ensure it belongs to this NGO
    project = next((p for p in admin_projects_data if p['id'] == project_id and p['ngo_name'] == ngo['name']), None)
    if not project:
        flash('Project not found or access denied', 'error')
        return redirect(url_for('ngo.ngo_drone_monitoring'))
    
    # Get coordinates for drone analysis
    if project.get('location'):
        try:
            # Try to parse coordinates if they're in lat,lon format
            location_parts = project['location'].split(',')
            if len(location_parts) >= 2 and all(part.replace('.', '').replace('-', '').isdigit() for part in location_parts[:2]):
                coords = [float(location_parts[0].strip()), float(location_parts[1].strip())]
            else:
                # Default coordinates for common cities
                location_mapping = {
                    'mumbai': [19.0760, 72.8777],
                    'chennai': [13.0827, 80.2707],
                    'kochi': [9.9312, 76.2673],
                    'kolkata': [22.5726, 88.3639],
                    'puri': [19.8135, 85.8312],
                    'delhi': [28.7041, 77.1025],
                    'bangalore': [12.9716, 77.5946]
                }
                city_name = location_parts[0].strip().lower()
                coords = location_mapping.get(city_name, [19.0760, 72.8777])  # Default to Mumbai
        except (ValueError, IndexError):
            coords = [19.0760, 72.8777]  # Default Mumbai coordinates
    else:
        coords = [19.0760, 72.8777]  # Default Mumbai coordinates
    
    # Generate comprehensive drone analysis report
    try:
        drone_report = drone_processor.get_comprehensive_drone_report(
            project_id=project_id,
            coordinates=coords
        )
        
        return render_template('ngo/drone_project_detail.html', 
                             project=project, 
                             drone_report=drone_report,
                             ngo=ngo)
        
    except Exception as e:
        flash(f'Error loading drone data: {str(e)}', 'error')
        return redirect(url_for('ngo.ngo_drone_monitoring'))

@admin_bp.route("/login", methods=['GET', 'POST'])
def admin_login():
    """NCCR Admin Login with proper authentication"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password, 'admin')
        if user:
            login_user(user)
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route("/")
@admin_bp.route("/dashboard")
@login_required(['admin'])
def admin_dashboard():
    """NCCR Admin Dashboard - Overview with comprehensive statistics"""
    generate_comprehensive_admin_data()
    
    # Calculate comprehensive statistics
    total_projects = len(admin_projects_data)
    pending_verification = len([p for p in admin_projects_data if p['status'] in ['Pending Review', 'Documents Missing', 'Under Verification']])
    verified_projects = len([p for p in admin_projects_data if p['status'] == 'Verified'])
    
    # Log real-time dashboard stats
    logger.info(f"ADMIN DASHBOARD: Total projects: {total_projects}, Pending: {pending_verification}, Verified: {verified_projects}")
    total_credits_generated = sum(p['credits_requested'] for p in admin_projects_data)
    total_credits_verified = sum(p['credits_approved'] for p in admin_projects_data if p['status'] == 'Verified')
    total_revenue_distributed = sum(t['total_value'] for t in transactions_data if t['status'] == 'Completed')
    
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
    activities = [
        {'title': 'New project "Sundarbans Mangrove Restoration" submitted', 'time': '2 hours ago', 'type': 'info'},
        {'title': 'Project PROJ1005 approved and credits issued', 'time': '4 hours ago', 'type': 'success'},
        {'title': 'NGO "Green Earth Foundation" verified successfully', 'time': '6 hours ago', 'type': 'success'},
        {'title': 'Industry "EcoTech Industries" purchased 150 credits', 'time': '8 hours ago', 'type': 'success'},
        {'title': 'Project PROJ1003 sent back for revision', 'time': '1 day ago', 'type': 'warning'},
        {'title': 'New industry "Carbon Neutral Ltd" registered', 'time': '1 day ago', 'type': 'info'}
    ]
    
    stats = {
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
    
    return render_template('admin/dashboard.html', stats=stats, activities=activities)

@admin_bp.route("/projects")
@login_required(['admin'])
def projects_management():
    """Projects Management - Main page with pending and verified tabs"""
    generate_comprehensive_admin_data()
    
    # Log current state for debugging
    logger.info(f"ADMIN PROJECTS VIEW: Total projects in system: {len(admin_projects_data)}")
    pending_projects = [p for p in admin_projects_data if p['status'] in ['Pending Review', 'Documents Missing', 'Under Verification']]
    verified_projects = [p for p in admin_projects_data if p['status'] == 'Verified']
    logger.info(f"ADMIN PROJECTS VIEW: Pending projects: {len(pending_projects)}, Verified projects: {len(verified_projects)}")
    
    # Log recent projects (last 5)
    recent_projects = sorted(admin_projects_data, key=lambda x: x.get('submission_date', datetime.now()), reverse=True)[:5]
    for proj in recent_projects:
        logger.info(f"RECENT PROJECT: {proj['id']} - {proj['name']} - Status: {proj['status']} - NGO: {proj['ngo_name']}")
    
    tab = request.args.get('tab', 'pending')  # pending or verified
    search = request.args.get('search', '')
    ecosystem_filter = request.args.get('ecosystem', '')
    status_filter = request.args.get('status', '')
    
    if tab == 'pending':
        projects = [p for p in admin_projects_data if p['status'] in ['Pending Review', 'Documents Missing', 'Under Verification']]
    else:
        projects = [p for p in admin_projects_data if p['status'] == 'Verified']
    
    # Apply filters
    if search:
        projects = [p for p in projects if search.lower() in p['name'].lower() or search.lower() in p['ngo_name'].lower() or search in p['id']]
    
    if ecosystem_filter:
        projects = [p for p in projects if p['ecosystem'] == ecosystem_filter]
    
    if status_filter:
        projects = [p for p in projects if p['status'] == status_filter]
    
    ecosystems = list(set(p['ecosystem'] for p in admin_projects_data))
    statuses = list(set(p['status'] for p in admin_projects_data))
    
    return render_template('admin/projects.html', 
                         projects=projects, 
                         tab=tab, 
                         search=search,
                         ecosystems=ecosystems,
                         statuses=statuses,
                         ecosystem_filter=ecosystem_filter,
                         status_filter=status_filter,
                         datetime=datetime)

@admin_bp.route("/projects/<project_id>")
@login_required(['admin'])
def project_details(project_id):
    """Detailed view of a specific project"""
    generate_comprehensive_admin_data()
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('admin.projects_management'))
    
    # Get NGO details
    ngo = next((n for n in admin_ngos_data if n['name'] == project['ngo_name']), None)
    
    return render_template('admin/project_details.html', project=project, ngo=ngo)

@admin_bp.route("/projects/<project_id>/action", methods=['POST'])
@login_required(['admin'])
def project_action(project_id):
    """Handle project actions (approve, reject, send back)"""
    generate_comprehensive_admin_data()
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'message': 'Project not found'})
    
    if action == 'approve':
        # Get approved credits amount from form
        approved_credits = float(request.form.get('approved_credits', project['credits_requested']))
        
        project['status'] = 'Verified'
        project['approval_date'] = datetime.now()
        project['credits_approved'] = approved_credits
        project['verification_notes'] = f'Approved: {reason}' if reason else 'Approved'
        
        # Mint tokens on blockchain
        try:
            blockchain_mrv.verify_project_on_blockchain(
                project_id=project_id,
                verifier_node='NCCR_Node_1',
                approval_data={
                    'status': 'approved',
                    'credits_approved': approved_credits,
                    'notes': reason or 'Project verified and approved'
                }
            )
            # Get blockchain token info
            blockchain_info = blockchain_mrv.get_project_blockchain_info(project_id)
            if blockchain_info and blockchain_info.get('token_ids'):
                project['token_id'] = blockchain_info['token_ids'][0]
                project['blockchain_verified'] = True
            else:
                project['token_id'] = f'BC{random.randint(100000, 999999)}'  # Fallback
                
        except Exception as e:
            project['token_id'] = f'BC{random.randint(100000, 999999)}'  # Fallback
            project['blockchain_error'] = str(e)
        
        message = f'Project {project_id} approved with {approved_credits} tCO₂e credits issued successfully'
        
    elif action == 'reject':
        project['status'] = 'Rejected'
        project['verification_notes'] = f'Rejected: {reason}'
        message = f'Project {project_id} rejected successfully'
        
    elif action == 'send_back':
        project['status'] = 'Documents Missing'
        project['verification_notes'] = f'Sent back for revision: {reason}'
        message = f'Project {project_id} sent back for revision'
    
    project['last_updated'] = datetime.now()
    
    return jsonify({'success': True, 'message': message})

@admin_bp.route("/projects/<project_id>/satellite")
def project_satellite_monitoring(project_id):
    """Get satellite monitoring data for a project"""
    generate_comprehensive_admin_data()
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'})
    
    try:
        # Get satellite monitoring data
        satellite_data = satellite_processor.monitor_restoration_site(project)
        
        # Get IoT sensor data if available
        if project.get('location'):
            coords = satellite_processor._extract_coordinates(project['location'])
            sensor_data = sensor_network.get_sensor_readings(project_id, coords)
        else:
            sensor_data = None
        
        return jsonify({
            'success': True,
            'satellite_monitoring': satellite_data,
            'sensor_data': sensor_data,
            'blockchain_info': blockchain_mrv.get_project_blockchain_info(project_id)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route("/projects/<project_id>/forecast")
def project_ml_forecast(project_id):
    """Get ML-based carbon sequestration forecast for a project"""
    generate_comprehensive_admin_data()
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'})
    
    try:
        # Get carbon sequestration forecast
        forecast_years = int(request.args.get('years', 20))
        carbon_forecast = ml_predictor.predict_carbon_sequestration(project, forecast_years)
        
        # Get ecosystem health prediction
        sensor_data = None
        if project.get('location'):
            coords = satellite_processor._extract_coordinates(project['location'])
            sensor_data = sensor_network.get_sensor_readings(project_id, coords)
        
        health_forecast = ml_predictor.predict_ecosystem_health(project, sensor_data)
        
        # Get optimal planting strategy recommendations
        site_conditions = {
            'location': satellite_processor._extract_coordinates(project.get('location', '19.0176,72.8562')),
            'area': project.get('area', 10.0),
            'soil': {'ph': 7.0, 'salinity': 5.0},
            'water': {'availability': 'high'}
        }
        planting_optimization = ml_predictor.optimize_planting_strategy(site_conditions)
        
        return jsonify({
            'success': True,
            'carbon_forecast': carbon_forecast,
            'health_forecast': health_forecast,
            'planting_optimization': planting_optimization
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Admin satellite/drone monitoring removed - these features are now NGO-only
# Redirects for any legacy admin links
@admin_bp.route("/satellite-monitoring")
@login_required(['admin'])
def satellite_monitoring():
    """Redirect to project management - satellite monitoring is NGO-only"""
    flash('Satellite monitoring is available in the NGO portal for project owners', 'info')
    return redirect(url_for('admin.projects_management'))

@admin_bp.route("/drone-monitoring")
@login_required(['admin'])
def drone_monitoring():
    """Redirect to project management - drone monitoring is NGO-only"""
    flash('Drone monitoring is available in the NGO portal for project owners', 'info')
    return redirect(url_for('admin.projects_management'))

@admin_bp.route("/blockchain/stats")
@login_required(['admin'])
def blockchain_statistics():
    """Get blockchain system statistics"""
    try:
        stats = blockchain_mrv.get_blockchain_stats()
        return jsonify({
            'success': True,
            'blockchain_stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route("/revenue")
def revenue_tracking():
    """Revenue Tracking Dashboard"""
    generate_comprehensive_admin_data()
    
    # Calculate revenue statistics
    total_revenue = sum(t['total_value'] for t in transactions_data if t['status'] == 'Completed')
    pending_revenue = sum(t['total_value'] for t in transactions_data if t['status'] in ['Pending', 'Processing'])
    failed_revenue = sum(t['total_value'] for t in transactions_data if t['status'] == 'Failed')
    total_transactions = len(transactions_data)
    completed_transactions = len([t for t in transactions_data if t['status'] == 'Completed'])
    
    # Filter transactions
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    filtered_transactions = transactions_data.copy()
    if status_filter:
        filtered_transactions = [t for t in filtered_transactions if t['status'] == status_filter]
    if search:
        filtered_transactions = [t for t in filtered_transactions if 
                               search.lower() in t['buyer_name'].lower() or 
                               search.lower() in t['project_name'].lower() or
                               search in t['id']]
    
    revenue_stats = {
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'failed_revenue': failed_revenue,
        'total_transactions': total_transactions,
        'completed_transactions': completed_transactions,
        'success_rate': round((completed_transactions / total_transactions * 100), 1) if total_transactions > 0 else 0
    }
    
    return render_template('admin/revenue.html', 
                         transactions=filtered_transactions,
                         stats=revenue_stats,
                         status_filter=status_filter,
                         search=search)





# Admin Industry Application Management Routes
@admin_bp.route("/industries/applications")
@login_required(['admin'])
def industry_applications():
    """Admin View of Industry Applications (Pending and All)"""
    generate_comprehensive_admin_data()
    
    tab = request.args.get('tab', 'pending')  # pending, approved, rejected, all
    search = request.args.get('search', '')
    sector_filter = request.args.get('sector', '')
    
    # Get all applications (including both applications and existing industries)
    all_applications = admin_industries_data.copy()
    
    # Filter by tab
    if tab == 'pending':
        applications = [app for app in all_applications if app['status'] == 'Pending']
    elif tab == 'approved':
        applications = [app for app in all_applications if app['status'] == 'Verified']
    elif tab == 'rejected':
        applications = [app for app in all_applications if app['status'] == 'Blacklisted']
    else:
        applications = all_applications
    
    # Apply filters
    if search:
        applications = [app for app in applications if 
                       search.lower() in app.get('company_name', app.get('name', '')).lower() or 
                       search.lower() in app.get('contact_person', '').lower() or
                       search in app['id']]
    
    if sector_filter:
        applications = [app for app in applications if 
                       app.get('industry_type', app.get('sector', '')) == sector_filter]
    
    # Get unique sectors for filter
    sectors = list(set(app.get('industry_type', app.get('sector', '')) for app in all_applications if app.get('industry_type', app.get('sector', ''))))
    
    # Calculate statistics
    stats = {
        'total': len(all_applications),
        'pending': len([app for app in all_applications if app['status'] == 'Pending']),
        'approved': len([app for app in all_applications if app['status'] == 'Verified']),
        'rejected': len([app for app in all_applications if app['status'] == 'Blacklisted'])
    }
    
    return render_template('admin/industry_applications.html',
                         applications=applications,
                         stats=stats,
                         tab=tab,
                         search=search,
                         sector_filter=sector_filter,
                         sectors=sectors,
                         datetime=datetime)

@admin_bp.route("/industries/applications/<app_id>")
@login_required(['admin'])
def industry_application_details(app_id):
    """Detailed view of a specific industry application"""
    generate_comprehensive_admin_data()
    
    application = next((app for app in admin_industries_data if app['id'] == app_id), None)
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('admin.industry_applications'))
    
    return render_template('admin/industry_application_details.html', application=application)

@admin_bp.route("/industries/applications/<app_id>/action", methods=['POST'])
@login_required(['admin'])
def industry_application_action(app_id):
    """Handle industry application actions (approve, reject, request more info)"""
    generate_comprehensive_admin_data()
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    admin_notes = request.form.get('admin_notes', '')
    
    application = next((app for app in admin_industries_data if app['id'] == app_id), None)
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'})
    
    if action == 'approve':
        application['status'] = 'Verified'
        application['approval_date'] = datetime.now()
        application['verification_date'] = datetime.now()
        application['verification_notes'] = f'Approved: {reason}' if reason else 'Application approved by admin'
        
        # Set up industry account with login credentials (in production, send email)
        # Generate login credentials and wallet setup would happen here
        
        message = f'Industry application for "{application.get("company_name", application.get("name", "Unknown"))}" approved successfully'
        
    elif action == 'reject':
        application['status'] = 'Blacklisted'
        application['verification_notes'] = f'Rejected: {reason}'
        application['rejection_reason'] = reason
        application['rejection_date'] = datetime.now()
        message = f'Industry application for "{application.get("company_name", application.get("name", "Unknown"))}" rejected'
        
    elif action == 'request_info':
        application['status'] = 'Under Review'
        application['verification_notes'] = f'Additional information requested: {reason}'
        application['info_requested_date'] = datetime.now()
        message = f'Additional information requested from "{application.get("company_name", application.get("name", "Unknown"))}"'
    
    # Add admin notes
    if admin_notes:
        if 'admin_notes_history' not in application:
            application['admin_notes_history'] = []
        application['admin_notes_history'].append({
            'note': admin_notes,
            'admin_name': get_current_user().get('name', 'Admin'),
            'timestamp': datetime.now()
        })
    
    application['last_updated'] = datetime.now()
    
    return jsonify({'success': True, 'message': message})

# Admin Management Routes
@admin_bp.route("/settings")
@login_required(['admin'])
def admin_settings():
    """Admin Settings Page"""
    return render_template('admin/settings.html')

@admin_bp.route("/admins")
@login_required(['admin'])
def admins_management():
    """Admin Users Management"""
    # Get all admin users from database
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, email, name, organization, created_at FROM users WHERE role = 'admin'")
    admins = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return render_template('admin/admins.html', admins=admins)

@admin_bp.route("/admins/new", methods=['GET', 'POST'])
@login_required(['admin'])
def add_new_admin():
    """Add New Admin"""
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            organization = request.form.get('organization', '').strip()
            department = request.form.get('department', '').strip()
            designation = request.form.get('designation', '').strip()
            phone = request.form.get('phone', '').strip()
            
            # Validation
            if not all([name, email, password, organization]):
                flash('Please fill in all required fields.', 'error')
                return render_template('admin/add_admin.html')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('admin/add_admin.html')
            
            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('admin/add_admin.html')
            
            # Check if email already exists
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                flash('Email already registered. Please use a different email.', 'error')
                conn.close()
                return render_template('admin/add_admin.html')
            
            # Create new admin user
            password_hash = generate_password_hash(password)
            now = datetime.utcnow().isoformat()
            
            cur.execute(
                "INSERT INTO users (email, password_hash, role, name, organization, created_at) VALUES (?,?,?,?,?,?)",
                (email, password_hash, 'admin', name, organization, now)
            )
            conn.commit()
            conn.close()
            
            # Log admin creation
            current_admin = get_current_user()
            flash(f'New admin "{name}" created successfully by {current_admin["name"]}.', 'success')
            
            return redirect(url_for('admin.admins_management'))
            
        except Exception as e:
            flash(f'Failed to create admin: {str(e)}', 'error')
            return render_template('admin/add_admin.html')
    
    return render_template('admin/add_admin.html')

@admin_bp.route("/admins/<int:admin_id>/delete", methods=['POST'])
@login_required(['admin'])
def delete_admin(admin_id):
    """Delete Admin (Only for super admin)"""
    try:
        current_admin = get_current_user()
        
        # Prevent self-deletion
        if current_admin['id'] == admin_id:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'})
        
        conn = get_conn()
        cur = conn.cursor()
        
        # Get admin details before deletion
        cur.execute("SELECT name FROM users WHERE id = ? AND role = 'admin'", (admin_id,))
        admin_to_delete = cur.fetchone()
        
        if not admin_to_delete:
            return jsonify({'success': False, 'message': 'Admin not found'})
        
        # Delete the admin
        cur.execute("DELETE FROM users WHERE id = ? AND role = 'admin'", (admin_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Admin "{admin_to_delete["name"]}" deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@admin_bp.route("/nccr-tools")
@login_required(['admin'])
def nccr_tools():
    """NCCR Admin Tools Dashboard - Advanced MRV Analytics"""
    generate_comprehensive_admin_data()
    
    try:
        # Get blockchain stats
        try:
            blockchain_stats = blockchain_mrv.get_blockchain_stats()
            # Ensure required attributes exist
            if not hasattr(blockchain_stats, 'total_supply'):
                blockchain_stats = {
                    'total_transactions': blockchain_stats.get('total_transactions', 0),
                    'total_tokens': blockchain_stats.get('total_tokens', 0),
                    'total_supply': blockchain_stats.get('total_supply', 0.0),
                    'available_supply': blockchain_stats.get('available_supply', 0.0),
                    'retired_supply': blockchain_stats.get('retired_supply', 0.0)
                }
        except Exception as e:
            logger.warning(f"Blockchain stats error: {e}")
            blockchain_stats = {
                'total_transactions': 0,
                'total_tokens': 0,
                'total_supply': 0.0,
                'available_supply': 0.0,
                'retired_supply': 0.0
            }
        
        # Calculate MRV analytics
        total_projects = len(admin_projects_data)
        verified_projects = len([p for p in admin_projects_data if p['status'] == 'Verified'])
        pending_projects = len([p for p in admin_projects_data if p['status'] in ['Pending Review', 'Under Verification']])
        
        # Calculate ecosystem distribution
        ecosystem_distribution = {}
        for project in admin_projects_data:
            ecosystem = project['ecosystem']
            ecosystem_distribution[ecosystem] = ecosystem_distribution.get(ecosystem, 0) + 1
        
        # Calculate state-wise distribution
        state_distribution = {}
        for project in admin_projects_data:
            state = project['state']
            state_distribution[state] = state_distribution.get(state, 0) + 1
        
        # NGO performance metrics
        ngo_performance = []
        for ngo in admin_ngos_data[:10]:  # Top 10 NGOs
            ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
            success_rate = len([p for p in ngo_projects if p['status'] == 'Verified']) / max(len(ngo_projects), 1) * 100
            ngo_performance.append({
                'name': ngo['name'],
                'projects_submitted': len(ngo_projects),
                'credits_earned': ngo['credits_earned'],
                'success_rate': round(success_rate, 1),
                'revenue': ngo['total_revenue']
            })
        
        # Monthly verification trends (mock data)
        monthly_trends = []
        for i in range(12, 0, -1):
            date = datetime.now() - timedelta(days=i*30)
            projects_verified = random.randint(5, 25)
            credits_issued = random.randint(200, 800)
            monthly_trends.append({
                'month': date.strftime('%b %Y'),
                'projects_verified': projects_verified,
                'credits_issued': credits_issued,
                'average_credits_per_project': round(credits_issued / max(projects_verified, 1), 1)
            })
        
        # Environmental impact metrics
        total_area_restored = sum(p['area'] for p in admin_projects_data if p['status'] == 'Verified')
        total_credits_issued = sum(p['credits_approved'] for p in admin_projects_data)
        estimated_co2_sequestered = total_credits_issued  # 1 credit = 1 tCO2e
        
        # Compliance and quality metrics
        compliance_metrics = {
            'vcs_compliant': len([p for p in admin_projects_data if 'VCS' in str(p.get('documents', []))]),
            'gold_standard': len([p for p in admin_projects_data if 'Gold' in str(p.get('documents', []))]),
            'documentation_complete': len([p for p in admin_projects_data if len(p.get('documents', [])) >= 3]),
            'verification_pending': pending_projects,
            'average_verification_time': random.randint(15, 45)  # days
        }
        
        # Risk and fraud detection metrics
        risk_metrics = {
            'high_risk_projects': random.randint(0, 3),
            'flagged_ngos': random.randint(0, 2),
            'document_anomalies': random.randint(0, 5),
            'location_duplicates': random.randint(0, 3),
            'trust_score_avg': round(random.uniform(85, 95), 1)
        }
        
        return render_template('admin/nccr_tools.html',
                             title='NCCR Admin Tools',
                             header='NCCR Advanced MRV Analytics',
                             active='nccr_tools',
                             # Summary metrics
                             total_projects=total_projects,
                             verified_projects=verified_projects,
                             pending_projects=pending_projects,
                             verification_rate=round((verified_projects / max(total_projects, 1)) * 100, 1),
                             # Environmental impact
                             total_area_restored=round(total_area_restored, 2),
                             total_credits_issued=total_credits_issued,
                             estimated_co2_sequestered=estimated_co2_sequestered,
                             # Analytics data
                             ecosystem_distribution=ecosystem_distribution,
                             state_distribution=state_distribution,
                             ngo_performance=ngo_performance,
                             monthly_trends=monthly_trends,
                             compliance_metrics=compliance_metrics,
                             risk_metrics=risk_metrics,
                             blockchain_stats=blockchain_stats,
                             # Totals
                             total_ngos=len(admin_ngos_data),
                             total_industries=len(admin_industries_data),
                             active_ngos=len([ngo for ngo in admin_ngos_data if ngo['status'] == 'Verified']))
        
    except Exception as e:
        logger.error(f"NCCR Tools error: {e}")
        flash('Error loading NCCR tools dashboard', 'error')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route("/export/<data_type>")
def export_data(data_type):
    """Export data to CSV"""
    generate_comprehensive_admin_data()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if data_type == 'projects':
        writer.writerow(['Project ID', 'Name', 'NGO', 'Location', 'Ecosystem', 'Area (ha)', 'Status', 'Credits', 'Submission Date'])
        for project in admin_projects_data:
            writer.writerow([
                project['id'], project['name'], project['ngo_name'], project['location'],
                project['ecosystem'], project['area'], project['status'], project['credits_requested'],
                project['submission_date'].strftime('%Y-%m-%d')
            ])
    elif data_type == 'ngos':
        writer.writerow(['NGO ID', 'Name', 'Status', 'Contact Person', 'Phone', 'Email', 'Credits Earned', 'Revenue'])
        for ngo in admin_ngos_data:
            writer.writerow([
                ngo['id'], ngo['name'], ngo['status'], ngo['contact_person'],
                ngo['phone'], ngo['email'], ngo['credits_earned'], ngo['total_revenue']
            ])
    elif data_type == 'industries':
        writer.writerow(['Industry ID', 'Name', 'Sector', 'Status', 'Contact Person', 'Credits Purchased', 'Revenue Contributed'])
        for industry in admin_industries_data:
            writer.writerow([
                industry['id'], industry['name'], industry['sector'], industry['status'],
                industry['contact_person'], industry['credits_purchased'], industry['revenue_contributed']
            ])
    
    output.seek(0)
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=nccr_{data_type}_export_{datetime.now().strftime("%Y%m%d")}.csv'
    return response

# Admin NGO Management Routes
@admin_bp.route("/ngos")
@login_required(['admin'])
def ngos_management():
    """NGO Management - View all NGOs and their approval status"""
    generate_comprehensive_admin_data()
    
    tab = request.args.get('tab', 'pending')
    search = request.args.get('search', '')
    
    if tab == 'pending':
        ngos = [ngo for ngo in admin_ngos_data if ngo['status'] == 'Pending']
    elif tab == 'verified':
        ngos = [ngo for ngo in admin_ngos_data if ngo['status'] == 'Verified']
    else:
        ngos = admin_ngos_data
    
    # Apply search filter
    if search:
        ngos = [ngo for ngo in ngos if search.lower() in ngo['name'].lower() 
                or search.lower() in ngo['email'].lower() 
                or search in ngo.get('registration_number', '')]
    
    # Calculate NGO statistics
    stats = {
        'total': len(admin_ngos_data),
        'verified': len([ngo for ngo in admin_ngos_data if ngo['status'] == 'Verified']),
        'pending': len([ngo for ngo in admin_ngos_data if ngo['status'] == 'Pending']),
        'blacklisted': len([ngo for ngo in admin_ngos_data if ngo['status'] == 'Blacklisted'])
    }
    
    return render_template('admin/ngos.html', 
                         ngos=ngos, 
                         stats=stats,
                         tab=tab, 
                         search=search,
                         datetime=datetime)

@admin_bp.route("/ngos/<ngo_id>/approve", methods=['POST'])
@login_required(['admin'])
def approve_ngo(ngo_id):
    """Approve NGO registration"""
    generate_comprehensive_admin_data()
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        return jsonify({'success': False, 'message': 'NGO not found'})
    
    notes = request.form.get('notes', '')
    
    # Update NGO status
    ngo['status'] = 'Verified'
    ngo['verification_date'] = datetime.now()
    ngo['verification_notes'] = f'Approved: {notes}' if notes else 'Approved by admin'
    
    # Send approval email
    try:
        email_system.send_ngo_approval_notification(
            email=ngo['email'],
            name=ngo['contact_person'],
            org_name=ngo['name']
        )
        logger.info(f"NGO approval email sent to {ngo['email']}")
    except Exception as e:
        logger.error(f"Failed to send NGO approval email: {e}")
    
    return jsonify({
        'success': True, 
        'message': f'NGO "{ngo["name"]}" approved successfully. Notification email sent.'
    })

@admin_bp.route("/ngos/<ngo_id>/reject", methods=['POST'])
@login_required(['admin'])
def reject_ngo(ngo_id):
    """Reject NGO registration"""
    generate_comprehensive_admin_data()
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        return jsonify({'success': False, 'message': 'NGO not found'})
    
    reason = request.form.get('reason', 'Registration requirements not met')
    
    # Update NGO status
    ngo['status'] = 'Rejected'
    ngo['verification_notes'] = f'Rejected: {reason}'
    
    # Send rejection email
    try:
        email_system.send_ngo_rejection_notification(
            email=ngo['email'],
            name=ngo['contact_person'],
            reason=reason
        )
        logger.info(f"NGO rejection email sent to {ngo['email']}")
    except Exception as e:
        logger.error(f"Failed to send NGO rejection email: {e}")
    
    return jsonify({
        'success': True, 
        'message': f'NGO "{ngo["name"]}" rejection processed. Notification email sent.'
    })

@admin_bp.route("/ngos/<ngo_id>/action", methods=['POST'])
@login_required(['admin'])
def ngo_action(ngo_id):
    """Handle NGO actions (verify, reject, blacklist, edit)"""
    generate_comprehensive_admin_data()
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        return jsonify({'success': False, 'message': 'NGO not found'})
    
    if action == 'verify':
        # Verify the NGO
        ngo['status'] = 'Verified'
        ngo['verification_date'] = datetime.now()
        ngo['verification_notes'] = f'Verified: {reason}' if reason else 'Verified by admin'
        
        # Send approval email
        try:
            email_system.send_ngo_approval_notification(
                email=ngo['email'],
                name=ngo['contact_person'],
                org_name=ngo['name']
            )
            logger.info(f"NGO approval email sent to {ngo['email']}")
        except Exception as e:
            logger.error(f"Failed to send NGO approval email: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'NGO "{ngo["name"]}" verified successfully. Notification email sent.'
        })
    
    elif action == 'reject':
        # Reject the NGO
        ngo['status'] = 'Rejected'
        ngo['verification_notes'] = f'Rejected: {reason}'
        ngo['rejection_date'] = datetime.now()
        
        # Send rejection email
        try:
            email_system.send_ngo_rejection_notification(
                email=ngo['email'],
                name=ngo['contact_person'],
                reason=reason
            )
            logger.info(f"NGO rejection email sent to {ngo['email']}")
        except Exception as e:
            logger.error(f"Failed to send NGO rejection email: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'NGO "{ngo["name"]}" rejected successfully. Notification email sent.'
        })
    
    elif action == 'blacklist':
        # Blacklist the NGO
        ngo['status'] = 'Blacklisted'
        ngo['verification_notes'] = f'Blacklisted: {reason}'
        ngo['blacklist_date'] = datetime.now()
        
        return jsonify({
            'success': True, 
            'message': f'NGO "{ngo["name"]}" blacklisted successfully.'
        })
    
    elif action == 'edit':
        # Update NGO information
        ngo['contact_person'] = request.form.get('contact_person', ngo['contact_person'])
        ngo['phone'] = request.form.get('phone', ngo['phone'])
        ngo['email'] = request.form.get('email', ngo['email'])
        ngo['last_updated'] = datetime.now()
        
        return jsonify({
            'success': True, 
            'message': f'NGO "{ngo["name"]}" information updated successfully.'
        })
    
    return jsonify({'success': False, 'message': 'Invalid action'})

@admin_bp.route("/ngos/<ngo_id>")
@login_required(['admin'])
def ngo_details(ngo_id):
    """NGO Details Page - View detailed information about a specific NGO"""
    generate_comprehensive_admin_data()
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        flash('NGO not found', 'error')
        return redirect(url_for('admin.ngos_management'))
    
    # Get NGO's projects and calculate additional stats
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    ngo_transactions = [t for t in transactions_data if t['ngo_name'] == ngo['name']]
    
    logger.info(f"Rendering admin NGO details template for NGO: {ngo['name']} (ID: {ngo_id})")
    
    return render_template('admin/ngo_details.html', 
                         ngo=ngo,
                         projects=ngo_projects,
                         transactions=ngo_transactions,
                         template_debug='admin_ngo_details')

# Admin Industry Management Routes
@admin_bp.route("/industries")
@login_required(['admin'])
def industries_management():
    """Industry Management - View all industries and their approval status"""
    generate_comprehensive_admin_data()
    
    tab = request.args.get('tab', 'pending')
    search = request.args.get('search', '')
    
    if tab == 'pending':
        industries = [ind for ind in admin_industries_data if ind['status'] == 'Pending']
    elif tab == 'verified':
        industries = [ind for ind in admin_industries_data if ind['status'] == 'Verified']
    else:
        industries = admin_industries_data
    
    # Apply search filter
    if search:
        industries = [ind for ind in industries if search.lower() in ind['name'].lower() 
                     or search.lower() in ind['email'].lower() 
                     or search in ind.get('cin', '')]
    
    # Calculate industry statistics
    stats = {
        'total': len(admin_industries_data),
        'verified': len([ind for ind in admin_industries_data if ind['status'] == 'Verified']),
        'pending': len([ind for ind in admin_industries_data if ind['status'] == 'Pending']),
        'total_credits_purchased': sum(ind['credits_purchased'] for ind in admin_industries_data),
        'total_revenue_generated': sum(ind['revenue_contributed'] for ind in admin_industries_data)
    }
    
    return render_template('admin/industries.html', 
                         industries=industries, 
                         stats=stats,
                         tab=tab, 
                         search=search,
                         datetime=datetime)

@admin_bp.route("/industries/<industry_id>/approve", methods=['POST'])
@login_required(['admin'])
def approve_industry(industry_id):
    """Approve industry registration"""
    generate_comprehensive_admin_data()
    
    industry = next((ind for ind in admin_industries_data if ind['id'] == industry_id), None)
    if not industry:
        return jsonify({'success': False, 'message': 'Industry not found'})
    
    notes = request.form.get('notes', '')
    
    # Update industry status
    industry['status'] = 'Verified'
    industry['verification_date'] = datetime.now()
    industry['verification_notes'] = f'Approved: {notes}' if notes else 'Approved by admin'
    
    # Create user account in database
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Check if user account already exists
        cur.execute("SELECT id FROM users WHERE email = ?", (industry['email'],))
        if not cur.fetchone():
            # Generate temporary password
            temp_password = f"TempPass{random.randint(1000, 9999)}"
            password_hash = generate_password_hash(temp_password)
            
            cur.execute(
                "INSERT INTO users (email, password_hash, role, name, organization, created_at) VALUES (?,?,?,?,?,?)",
                (industry['email'], password_hash, 'industry', industry['contact_person'], industry['name'], datetime.utcnow().isoformat())
            )
            conn.commit()
            logger.info(f"Industry account created for {industry['email']}")
        
        conn.close()
    except Exception as e:
        logger.error(f"Failed to create industry user account: {e}")
        return jsonify({'success': False, 'message': 'Failed to create user account'})
    
    return jsonify({
        'success': True, 
        'message': f'Industry "{industry["name"]}" approved successfully.'
    })

@admin_bp.route("/industries/<industry_id>/reject", methods=['POST'])
@login_required(['admin'])
def reject_industry(industry_id):
    """Reject industry registration"""
    generate_comprehensive_admin_data()
    
    industry = next((ind for ind in admin_industries_data if ind['id'] == industry_id), None)
    if not industry:
        return jsonify({'success': False, 'message': 'Industry not found'})
    
    reason = request.form.get('reason', 'Registration requirements not met')
    
    # Update industry status
    industry['status'] = 'Rejected'
    industry['verification_notes'] = f'Rejected: {reason}'
    
    return jsonify({
        'success': True, 
        'message': f'Industry "{industry["name"]}" rejected successfully.'
    })

@admin_bp.route("/industries/<industry_id>/action", methods=['POST'])
@login_required(['admin'])
def industry_action(industry_id):
    """Handle industry actions (verify, reject, blacklist, edit)"""
    generate_comprehensive_admin_data()
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    industry = next((ind for ind in admin_industries_data if ind['id'] == industry_id), None)
    
    if not industry:
        return jsonify({'success': False, 'message': 'Industry not found'})
    
    if action == 'verify':
        # Verify the industry
        industry['status'] = 'Verified'
        industry['verification_date'] = datetime.now()
        industry['verification_notes'] = f'Verified: {reason}' if reason else 'Verified by admin'
        
        # Create user account in database
        try:
            conn = get_conn()
            cur = conn.cursor()
            
            # Check if user account already exists
            cur.execute("SELECT id FROM users WHERE email = ?", (industry['email'],))
            if not cur.fetchone():
                # Generate temporary password
                temp_password = f"TempPass{random.randint(1000, 9999)}"
                password_hash = generate_password_hash(temp_password)
                
                cur.execute(
                    "INSERT INTO users (email, password_hash, role, name, organization, created_at) VALUES (?,?,?,?,?,?)",
                    (industry['email'], password_hash, 'industry', industry['contact_person'], industry['name'], datetime.utcnow().isoformat())
                )
                conn.commit()
                logger.info(f"Industry account created for {industry['email']}")
            
            conn.close()
        except Exception as e:
            logger.error(f"Failed to create industry user account: {e}")
            return jsonify({'success': False, 'message': 'Failed to create user account'})
        
        return jsonify({
            'success': True, 
            'message': f'Industry "{industry["name"]}" verified successfully. User account created.'
        })
    
    elif action == 'reject':
        # Reject the industry
        industry['status'] = 'Rejected'
        industry['verification_notes'] = f'Rejected: {reason}'
        industry['rejection_date'] = datetime.now()
        
        return jsonify({
            'success': True, 
            'message': f'Industry "{industry["name"]}" rejected successfully.'
        })
    
    elif action == 'blacklist':
        # Blacklist the industry
        industry['status'] = 'Blacklisted'
        industry['verification_notes'] = f'Blacklisted: {reason}'
        industry['blacklist_date'] = datetime.now()
        
        return jsonify({
            'success': True, 
            'message': f'Industry "{industry["name"]}" blacklisted successfully.'
        })
    
    elif action == 'edit':
        # Update industry information
        industry['contact_person'] = request.form.get('contact_person', industry['contact_person'])
        industry['phone'] = request.form.get('phone', industry['phone'])
        industry['email'] = request.form.get('email', industry['email'])
        industry['last_updated'] = datetime.now()
        
        return jsonify({
            'success': True, 
            'message': f'Industry "{industry["name"]}" information updated successfully.'
        })
    
    return jsonify({'success': False, 'message': 'Invalid action'})

@admin_bp.route("/industries/<industry_id>")
@login_required(['admin'])
def industry_details(industry_id):
    """Industry Details Page - View detailed information about a specific industry"""
    generate_comprehensive_admin_data()
    
    industry = next((ind for ind in admin_industries_data if ind['id'] == industry_id), None)
    if not industry:
        flash('Industry not found', 'error')
        return redirect(url_for('admin.industries_management'))
    
    logger.info(f"Rendering admin Industry details template for Industry: {industry['name']} (ID: {industry_id})")
    
    return render_template('admin/industry_details.html', 
                         industry=industry,
                         template_debug='admin_industry_details')

@app.route("/register", methods=['GET', 'POST'])
def role_based_register():
    """Role-based User Registration System"""
    if request.method == 'POST':
        try:
            # Extract common form data
            role = request.form.get('role', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            phone = request.form.get('phone', '').strip()
            
            # Role-specific data
            role_specific_data = {}
            
            if role == 'admin':
                role_specific_data = {
                    'department': request.form.get('department', '').strip(),
                    'organization': 'NCCR'
                }
            elif role == 'auditor':
                role_specific_data = {
                    'license_number': request.form.get('license_number', '').strip(),
                    'experience': request.form.get('experience', ''),
                    'organization': 'Independent Auditor'
                }
            elif role == 'buyer':
                role_specific_data = {
                    'buyer_type': request.form.get('buyer_type', '').strip(),
                    'company_name': request.form.get('company_name', '').strip(),
                    'organization': request.form.get('company_name', '').strip() or 'Individual Buyer'
                }
            elif role == 'seller':
                role_specific_data = {
                    'organization': request.form.get('organization', '').strip(),
                    'project_types': request.form.get('project_types', '').strip()
                }
            elif role == 'industry_rep':
                role_specific_data = {
                    'company_name': request.form.get('company_name', '').strip(),
                    'designation': request.form.get('designation', '').strip(),
                    'employee_id': request.form.get('employee_id', '').strip(),
                    'organization': request.form.get('company_name', '').strip()
                }
            
            # Validation
            if not all([role, name, email, password, phone]):
                return jsonify({
                    'success': False,
                    'message': 'Please fill in all required fields.'
                })
            
            if len(password) < 8:
                return jsonify({
                    'success': False,
                    'message': 'Password must be at least 8 characters long.'
                })
            
            # Check if email already exists
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                conn.close()
                return jsonify({
                    'success': False,
                    'message': 'Email already registered. Please use a different email.'
                })
            
            # Handle file uploads (store file names for now)
            uploaded_files = {}
            for key, file in request.files.items():
                if file.filename:
                    # In production, save files to secure location
                    filename = f"{role}_{email}_{key}_{file.filename}"
                    file_path = os.path.join(UPLOADS_FOLDER, filename)
                    file.save(file_path)
                    uploaded_files[key] = filename
            
            # Create new user account
            password_hash = generate_password_hash(password)
            now = datetime.utcnow().isoformat()
            
            # Set initial status based on role
            status = 'Pending'  # All roles require verification except admin
            if role == 'admin':
                status = 'Pending'  # Even admins need approval from existing admin
            
            cur.execute(
                "INSERT INTO users (email, password_hash, role, name, organization, phone, status, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (email, password_hash, role, name, role_specific_data.get('organization', ''), phone, status, now)
            )
            user_id = cur.lastrowid
            
            # Store role-specific data and files info in a separate table (simulate with JSON for now)
            user_profile = {
                'user_id': user_id,
                'role': role,
                'role_data': role_specific_data,
                'uploaded_files': uploaded_files,
                'registration_date': now,
                'verification_status': status
            }
            
            # In production, store this in a proper profiles table
            # For now, we'll add it to a simple storage
            if not hasattr(app, 'user_profiles'):
                app.user_profiles = []
            app.user_profiles.append(user_profile)
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Registration successful! Your {role} account is pending verification.',
                'user_id': user_id
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            })
    
    return render_template('register.html')

@app.route("/login")
def unified_login():
    """Unified Login Page for All Roles"""
    return render_template('login.html')

@app.route("/")
def public_landing_page():
    """Public Landing Page - Welcome page for visitors"""
    return render_template("public_home.html")

@app.route("/index")
def index_redirect():
    """Redirect old index route to landing page"""
    return redirect(url_for('public_landing_page'))

@app.route("/dashboard")
def dashboard_redirect():
    """Redirect to appropriate dashboard based on session"""
    if 'user_role' not in session:
        return redirect(url_for('unified_login'))
    
    role = session['user_role']
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'ngo':
        return redirect(url_for('ngo.dashboard'))
    elif role == 'industry':
        return redirect(url_for('industry.dashboard'))
    else:
        return redirect(url_for('public_landing_page'))

@app.route("/logout")
def logout():
    """Universal logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('public_landing_page'))

@app.route("/_routes")
def list_routes():
    lines = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        lines.append(f"{methods}\t{rule.endpoint}\t{rule}")
    return Response("\n".join(sorted(lines)), mimetype="text/plain")

# Industry data storage
industry_user_data = {
    'company_name': 'EcoTech Industries Ltd',
    'industry_type': 'Manufacturing',
    'contact_person': 'John Smith',
    'email': 'john.smith@ecotech.com',
    'phone': '+91-9876543210',
    'address': '123 Industrial Area, Sector 18, Gurgaon, Haryana',
    'annual_emissions': 5000,  # tCO2e
    'credits_purchased': 2500,
    'credits_active': 1200,
    'credits_retired': 1300,
    'total_spent': 625000,  # Rs
    'wallet_balance': 1500000,  # Rs - Available balance for purchases
    'wallet_address': '0x742d35Cc6634C0532925a3b8D4B4B83b4B6E0772',
    'registration_date': datetime.now() - timedelta(days=365),
    'verification_status': 'Verified'
}

# Available projects for marketplace
marketplace_projects = [
    {
        'id': 'PROJ1001',
        'name': 'Sundarbans Mangrove Restoration',
        'location': 'West Bengal, India',
        'ngo': 'Green Earth Foundation',
        'ecosystem': 'Mangrove',
        'available_credits': 850,
        'price_per_credit': 250,
        'co_benefits': ['Biodiversity Conservation', 'Community Employment', 'Coastal Protection'],
        'image': '/static/images/mangrove.jpg',
        'verification': 'Gold Standard',
        'sdg_goals': [13, 14, 15, 8],
        'project_start': '2023-01-15',
        'methodology': 'VM0007 - REDD+ Methodology Framework'
    },
    {
        'id': 'PROJ1002', 
        'name': 'Kerala Seagrass Conservation',
        'location': 'Kerala, India',
        'ngo': 'Marine Life Protection Society',
        'ecosystem': 'Seagrass',
        'available_credits': 650,
        'price_per_credit': 280,
        'co_benefits': ['Marine Biodiversity', 'Fisheries Support', 'Water Quality'],
        'image': '/static/images/seagrass.jpg',
        'verification': 'Verra VCS',
        'sdg_goals': [13, 14, 1, 2],
        'project_start': '2023-03-20',
        'methodology': 'VM0033 - Methodology for Tidal Wetland'
    },
    {
        'id': 'PROJ1003',
        'name': 'Tamil Nadu Blue Carbon Initiative', 
        'location': 'Tamil Nadu, India',
        'ngo': 'Coastal Conservation Trust',
        'ecosystem': 'Coastal Wetlands',
        'available_credits': 1200,
        'price_per_credit': 220,
        'co_benefits': ['Storm Protection', 'Fish Nurseries', 'Tourism'],
        'image': '/static/images/wetlands.jpg',
        'verification': 'Gold Standard',
        'sdg_goals': [13, 14, 11, 8],
        'project_start': '2023-02-10', 
        'methodology': 'VM0024 - Methodology for Coastal Wetland Creation'
    }
]

# Industry purchase history
industry_purchases = [
    {
        'transaction_id': 'TXN100001',
        'project_name': 'Sundarbans Mangrove Restoration',
        'project_id': 'PROJ1001',
        'credits_purchased': 500,
        'price_per_credit': 250,
        'total_paid': 125000,
        'purchase_date': datetime.now() - timedelta(days=45),
        'status': 'Active',
        'token_id': 'BC789012',
        'blockchain_hash': '0x8a2b1c3d4e5f6789abc123def456789012345678901234567890abcdef123456',
        'retirement_date': None
    },
    {
        'transaction_id': 'TXN100002',
        'project_name': 'Kerala Seagrass Conservation',
        'project_id': 'PROJ1002', 
        'credits_purchased': 300,
        'price_per_credit': 280,
        'total_paid': 84000,
        'purchase_date': datetime.now() - timedelta(days=30),
        'status': 'Active',
        'token_id': 'BC789013',
        'blockchain_hash': '0x9b3c2d4e5f6789abc123def456789012345678901234567890abcdef234567',
        'retirement_date': None
    }
]

# Industry blueprint
industry_bp = Blueprint("industry", __name__, url_prefix="/industry")

@industry_bp.route("/")
def industry_index():
    """Industry Portal Landing Page"""
    return render_template('industry/index.html')

@industry_bp.route("/login", methods=['GET', 'POST'])
def industry_login():
    """Industry Login with proper authentication"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Industry login attempt: {email}")
        
        user = authenticate_user(email, password, 'industry')
        if user:
            print(f"Industry authentication successful for: {email}")
            # Generate data to ensure industry data exists
            generate_comprehensive_admin_data()
            
            # Check if industry is approved
            industry_data = next((ind for ind in admin_industries_data if ind['email'] == email), None)
            
            if industry_data:
                print(f"Found industry data for {email}: status={industry_data['status']}")
            else:
                print(f"No industry data found for {email}")
            
            if industry_data and industry_data['status'] == 'Pending':
                flash('Your account is still pending admin approval. Please wait for verification.', 'warning')
                return render_template('industry/login.html')
            
            login_user(user)
            print(f"Industry user logged in: {email}")
            flash('Welcome back!', 'success')
            return redirect(url_for('industry.dashboard'))
        else:
            print(f"Industry authentication failed for: {email}")
            flash('Invalid email or password.', 'error')
    
    return render_template('industry/login.html')

@industry_bp.route("/logout")
def industry_logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public_landing_page'))

@industry_bp.route("/dashboard")
@login_required(['industry'])
def dashboard():
    """Industry Dashboard"""
    # Generate data to ensure industry data exists
    generate_comprehensive_admin_data()
    
    # Check if industry is approved
    user_email = session.get('user_email')
    print(f"Industry dashboard access attempt by: {user_email}")
    
    industry_data = next((ind for ind in admin_industries_data if ind['email'] == user_email), None)
    
    if industry_data:
        print(f"Found industry data for {user_email}: status={industry_data['status']}")
    else:
        print(f"No industry data found for {user_email}. Available emails: {[ind['email'] for ind in admin_industries_data[:5]]}")
    
    if not industry_data or industry_data['status'] != 'Verified':
        flash('Access denied. Your industry registration is pending admin approval.', 'warning')
        logout_user()
        return redirect(url_for('industry.industry_login'))
    
    # Calculate dashboard stats
    total_credits = industry_user_data['credits_purchased']
    active_credits = industry_user_data['credits_active'] 
    offset_percentage = round((industry_user_data['credits_purchased'] / industry_user_data['annual_emissions']) * 100, 1)
    
    stats = {
        'credits_purchased': total_credits,
        'active_credits': active_credits,
        'total_revenue_contributed': industry_user_data['total_spent'],
        'offset_percentage': offset_percentage,
        'annual_emissions': industry_user_data['annual_emissions'],
        'credits_retired': industry_user_data['credits_retired']
    }
    
    recent_purchases = sorted(industry_purchases, key=lambda x: x['purchase_date'], reverse=True)[:5]
    
    return render_template('industry/dashboard.html', 
                         stats=stats, 
                         recent_purchases=recent_purchases,
                         company_name=industry_user_data['company_name'])

@industry_bp.route("/marketplace")
def marketplace():
    """Carbon Credits Marketplace"""
    return render_template('industry/marketplace.html', projects=marketplace_projects)

@industry_bp.route("/marketplace/buy/<project_id>", methods=['GET', 'POST'])
def buy_credits(project_id):
    """Buy carbon credits from a project"""
    project = next((p for p in marketplace_projects if p['id'] == project_id), None)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('industry.marketplace'))
    
    if request.method == 'POST':
        try:
            credits = int(request.form.get('credits', 0))
            payment_method = request.form.get('payment_method', 'wallet')
            
            # Validation checks
            if credits <= 0:
                return jsonify({'success': False, 'message': 'Credit amount must be greater than zero'})
            
            if credits > project['available_credits']:
                return jsonify({'success': False, 'message': f'Only {project["available_credits"]} credits available for this project'})
            
            # Check user balance for wallet payments
            total_cost = credits * project['price_per_credit']
            if payment_method == 'wallet':
                current_balance = industry_user_data.get('wallet_balance', 0)
                if current_balance < total_cost:
                    return jsonify({
                        'success': False, 
                        'message': f'Insufficient wallet balance. Required: ₹{total_cost:,}, Available: ₹{current_balance:,}'
                    })
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid credit amount format'})
        
        # Create purchase record
        total_cost = credits * project['price_per_credit']
        purchase = {
            'transaction_id': f'TXN{random.randint(100000, 999999)}',
            'project_name': project['name'],
            'project_id': project['id'],
            'credits_purchased': credits,
            'price_per_credit': project['price_per_credit'],
            'total_paid': total_cost,
            'purchase_date': datetime.now(),
            'status': 'Active',
            'token_id': f'BC{random.randint(100000, 999999)}',
            'blockchain_hash': f'0x{random.randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):040x}',
            'retirement_date': None
        }
        
        industry_purchases.append(purchase)
        
        # Update project availability
        project['available_credits'] -= credits
        
        # Deduct wallet balance for wallet payments
        if payment_method == 'wallet':
            industry_user_data['wallet_balance'] -= total_cost
        
        # Update industry stats
        industry_user_data['credits_purchased'] += credits
        industry_user_data['credits_active'] += credits
        industry_user_data['total_spent'] += total_cost
        
        # REAL-TIME NGO REVENUE UPDATE
        try:
            # Find the NGO that owns this project and update their revenue
            project_owner_ngo = next((n for n in admin_ngos_data if n['name'] == project['ngo_name']), None)
            if project_owner_ngo:
                # Calculate NGO's share (typically 70-80% of credit sale value)
                ngo_revenue_share = total_cost * 0.75  # 75% goes to NGO
                
                # Update NGO's revenue data
                if 'total_revenue' not in project_owner_ngo:
                    project_owner_ngo['total_revenue'] = 0
                if 'credits_sold' not in project_owner_ngo:
                    project_owner_ngo['credits_sold'] = 0
                    
                project_owner_ngo['total_revenue'] += ngo_revenue_share
                project_owner_ngo['credits_sold'] += credits
                project_owner_ngo['last_sale_date'] = datetime.now()
                
                # Update the specific project's sales data
                project_in_admin_data = next((p for p in admin_projects_data if p['id'] == project_id), None)
                if project_in_admin_data:
                    if 'revenue_generated' not in project_in_admin_data:
                        project_in_admin_data['revenue_generated'] = 0
                    if 'credits_sold' not in project_in_admin_data:
                        project_in_admin_data['credits_sold'] = 0
                        
                    project_in_admin_data['revenue_generated'] += ngo_revenue_share
                    project_in_admin_data['credits_sold'] += credits
                    project_in_admin_data['last_sale_date'] = datetime.now()
                
                # Add transaction to global transactions data for admin tracking
                transaction_record = {
                    'id': f'REV{random.randint(100000, 999999)}',
                    'transaction_id': purchase['transaction_id'],
                    'type': 'Credit Sale',
                    'ngo_name': project['ngo_name'],
                    'ngo_id': project_owner_ngo['id'],
                    'industry_name': industry_user_data.get('company_name', 'Demo Industry'),
                    'project_name': project['name'],
                    'project_id': project_id,
                    'credits_sold': credits,
                    'total_value': ngo_revenue_share,
                    'price_per_credit': project['price_per_credit'],
                    'sale_date': datetime.now(),
                    'status': 'Completed'
                }
                transactions_data.append(transaction_record)
                
                logger.info(f"✅ REAL-TIME UPDATE: NGO '{project['ngo_name']}' earned ₹{ngo_revenue_share:,.2f} from {credits} credit sale")
            else:
                logger.warning(f"NGO '{project['ngo_name']}' not found for revenue update")
                
        except Exception as e:
            logger.error(f"Failed to update NGO revenue: {e}")
        
        # Send credit purchase notifications
        try:
            # Get NGO email for this project
            ngo = next((n for n in admin_ngos_data if n['name'] == project['ngo_name']), None)
            ngo_email = ngo['email'] if ngo else 'ngo@example.com'
            
            # Send notifications to all stakeholders
            admin_email = getattr(email_system, 'admin_email', 'admin@bluecarbon.mrv')
            industry_email = getattr(industry_user_data, 'email', 'industry@example.com')
            industry_name = getattr(industry_user_data, 'company_name', 'Demo Industry')
            
            email_system.send_credits_purchase_notification(
                ngo_email=ngo_email,
                industry_email=industry_email,
                admin_email=admin_email,
                ngo_name=project['ngo_name'],
                industry_name=industry_name,
                project_name=project['name'],
                credits=credits,
                total_amount=total_cost,
                transaction_id=purchase['transaction_id']
            )
            logger.info(f"Credit purchase notifications sent for transaction {purchase['transaction_id']}")
        except Exception as e:
            logger.error(f"Failed to send credit purchase notifications: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully purchased {credits} credits for ₹{total_cost:,}. Notifications sent to all parties.',
            'transaction_id': purchase['transaction_id']
        })
    
    return render_template('industry/buy_credits.html', project=project)

@industry_bp.route("/credits")
def credits():
    """View purchased credits"""
    return render_template('industry/credits.html', 
                         purchases=industry_purchases,
                         stats=industry_user_data)

@industry_bp.route("/credits/retire/<transaction_id>", methods=['POST'])
def retire_credits(transaction_id):
    """Retire carbon credits for offsetting"""
    purchase = next((p for p in industry_purchases if p['transaction_id'] == transaction_id), None)
    if not purchase:
        return jsonify({'success': False, 'message': 'Transaction not found'})
    
    if purchase['status'] == 'Retired':
        return jsonify({'success': False, 'message': 'Credits already retired'})
    
    # Retire the credits
    purchase['status'] = 'Retired'
    purchase['retirement_date'] = datetime.now()
    
    # Update industry stats
    industry_user_data['credits_active'] -= purchase['credits_purchased']
    industry_user_data['credits_retired'] += purchase['credits_purchased']
    
    return jsonify({
        'success': True,
        'message': f'Successfully retired {purchase["credits_purchased"]} credits'
    })

@industry_bp.route("/footprint")
def footprint():
    """Carbon footprint tracker"""
    offset_data = {
        'annual_emissions': industry_user_data['annual_emissions'],
        'credits_purchased': industry_user_data['credits_purchased'],
        'credits_retired': industry_user_data['credits_retired'],
        'offset_percentage': round((industry_user_data['credits_retired'] / industry_user_data['annual_emissions']) * 100, 1),
        'remaining_emissions': industry_user_data['annual_emissions'] - industry_user_data['credits_retired']
    }
    
    return render_template('industry/footprint.html', offset_data=offset_data)

@industry_bp.route("/profile")
def profile():
    """Industry profile and settings"""
    return render_template('industry/profile.html', company=industry_user_data)

@industry_bp.route("/profile/update", methods=['POST'])
def update_profile():
    """Update industry profile"""
    industry_user_data['contact_person'] = request.form.get('contact_person', industry_user_data['contact_person'])
    industry_user_data['email'] = request.form.get('email', industry_user_data['email'])
    industry_user_data['phone'] = request.form.get('phone', industry_user_data['phone'])
    industry_user_data['address'] = request.form.get('address', industry_user_data['address'])
    industry_user_data['annual_emissions'] = int(request.form.get('annual_emissions', industry_user_data['annual_emissions']))
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@industry_bp.route("/reports")
def reports():
    """Reports and compliance page"""
    return render_template('industry/reports.html', 
                         purchases=industry_purchases,
                         company=industry_user_data)

@industry_bp.route("/help")
def help_support():
    """Help and Support Page"""
    return render_template('industry/help.html')

@industry_bp.route("/marketplace-p2p")
@login_required(['industry'])
def marketplace_p2p():
    """Industry-to-Industry Credit Marketplace"""
    generate_comprehensive_admin_data()
    
    # Check if industry is approved
    user_email = session.get('user_email')
    industry_data = next((ind for ind in admin_industries_data if ind['email'] == user_email), None)
    
    if not industry_data or industry_data['status'] != 'Verified':
        flash('Access denied. Your industry registration is pending admin approval.', 'warning')
        logout_user()
        return redirect(url_for('industry.industry_login'))
    
    return render_template('industry/marketplace_p2p.html')

@industry_bp.route("/marketplace-p2p/listings", methods=['GET'])
@login_required(['industry'])
def get_marketplace_listings():
    """Get all marketplace listings"""
    # Sample marketplace data - in production, get from database
    listings = [
        {
            'id': 'LIST001',
            'seller': 'TechCorp Industries',
            'sellerId': 'IND001',
            'project': 'Mumbai Mangrove Restoration',
            'ecosystem': 'Mangrove',
            'creditsAvailable': 500,
            'pricePerCredit': 250,
            'totalValue': 125000,
            'verification': 'Gold Standard',
            'created': '2024-01-15',
            'description': 'High-quality mangrove restoration credits with full verification'
        },
        {
            'id': 'LIST002',
            'seller': 'GreenEnergy Corp',
            'sellerId': 'IND002',
            'project': 'Kerala Seagrass Conservation',
            'ecosystem': 'Seagrass',
            'creditsAvailable': 750,
            'pricePerCredit': 280,
            'totalValue': 210000,
            'verification': 'VCS Verified',
            'created': '2024-01-20',
            'description': 'Premium seagrass conservation credits from Kerala backwaters'
        }
    ]
    
    return jsonify({'success': True, 'listings': listings})

@industry_bp.route("/marketplace-p2p/create-listing", methods=['POST'])
@login_required(['industry'])
def create_marketplace_listing():
    """Create a new marketplace listing"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        user_email = session.get('user_email')
        industry_data = next((ind for ind in admin_industries_data if ind['email'] == user_email), None)
        
        if not industry_data:
            return jsonify({'success': False, 'message': 'Industry not found'})
        
        # Validate required fields
        required_fields = ['project_id', 'credits_to_sell', 'price_per_credit']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'})
        
        # Create listing (in production, save to database)
        listing_id = f'LIST{random.randint(100000, 999999)}'
        new_listing = {
            'id': listing_id,
            'seller': industry_data['name'],
            'seller_id': industry_data['id'],
            'seller_email': user_email,
            'project_id': data['project_id'],
            'project_name': data.get('project_name', 'Project'),
            'ecosystem': data.get('ecosystem', 'Mangrove'),
            'credits_to_sell': int(data['credits_to_sell']),
            'price_per_credit': float(data['price_per_credit']),
            'total_value': int(data['credits_to_sell']) * float(data['price_per_credit']),
            'description': data.get('description', ''),
            'listing_duration': int(data.get('listing_duration', 14)),
            'status': 'Active',
            'created_date': datetime.now(),
            'verification': 'Gold Standard'  # Default
        }
        
        # In production, save to marketplace listings database
        logger.info(f"Marketplace listing created: {listing_id} by {industry_data['name']}")
        
        return jsonify({
            'success': True,
            'message': 'Listing created successfully!',
            'listing_id': listing_id,
            'listing': new_listing
        })
        
    except Exception as e:
        logger.error(f"Failed to create marketplace listing: {e}")
        return jsonify({'success': False, 'message': 'Failed to create listing'})

@industry_bp.route("/marketplace-p2p/purchase", methods=['POST'])
@login_required(['industry'])
def purchase_from_marketplace():
    """Purchase credits from marketplace"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        user_email = session.get('user_email')
        buyer_data = next((ind for ind in admin_industries_data if ind['email'] == user_email), None)
        
        if not buyer_data:
            return jsonify({'success': False, 'message': 'Buyer industry not found'})
        
        # Validate purchase data
        listing_id = data.get('listing_id')
        quantity = int(data.get('quantity', 0))
        payment_method = data.get('payment_method', 'wallet')
        
        if not listing_id or quantity <= 0:
            return jsonify({'success': False, 'message': 'Invalid purchase data'})
        
        # In production, get listing from database and validate availability
        # For demo, simulate purchase
        total_cost = quantity * 250  # Sample price
        
        # Check wallet balance if using wallet payment
        if payment_method == 'wallet':
            current_balance = industry_user_data.get('wallet_balance', 0)
            if current_balance < total_cost:
                return jsonify({
                    'success': False,
                    'message': f'Insufficient wallet balance. Required: ₹{total_cost:,}, Available: ₹{current_balance:,}'
                })
            
            # Deduct from wallet
            industry_user_data['wallet_balance'] -= total_cost
        
        # Update buyer's credits
        industry_user_data['credits_purchased'] += quantity
        industry_user_data['credits_active'] += quantity
        industry_user_data['total_spent'] += total_cost
        
        # Create transaction record
        transaction_id = f'P2P{random.randint(100000, 999999)}'
        transaction_record = {
            'transaction_id': transaction_id,
            'type': 'P2P Purchase',
            'listing_id': listing_id,
            'buyer_id': buyer_data['id'],
            'buyer_name': buyer_data['name'],
            'seller_name': 'Demo Seller',  # In production, get from listing
            'project_name': 'Demo Project',
            'credits_purchased': quantity,
            'price_per_credit': 250,
            'total_cost': total_cost,
            'payment_method': payment_method,
            'purchase_date': datetime.now(),
            'status': 'Completed'
        }
        
        # In production, save transaction to database
        logger.info(f"P2P purchase completed: {transaction_id}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully purchased {quantity} credits for ₹{total_cost:,}',
            'transaction_id': transaction_id,
            'new_wallet_balance': industry_user_data.get('wallet_balance', 0)
        })
        
    except Exception as e:
        logger.error(f"Failed to process P2P purchase: {e}")
        return jsonify({'success': False, 'message': 'Purchase failed. Please try again.'})

@industry_bp.route("/wallet/topup", methods=['POST'])
def wallet_topup():
    """Top-up wallet balance"""
    try:
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method', 'bank')
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than zero'})
        
        if amount > 10000000:  # Max 1 crore per transaction
            return jsonify({'success': False, 'message': 'Maximum top-up amount is ₹1,00,00,000 per transaction'})
        
        # Simulate payment processing (in production, integrate with payment gateway)
        import random
        payment_success = random.choice([True, True, True, False])  # 75% success rate
        
        if payment_success:
            # Add to wallet balance
            industry_user_data['wallet_balance'] += amount
            
            return jsonify({
                'success': True,
                'message': f'Wallet topped up successfully with ₹{amount:,}',
                'new_balance': industry_user_data['wallet_balance']
            })
        else:
            # Payment failed - amount should not be deducted in real scenario
            return jsonify({
                'success': False,
                'message': 'Payment failed. Please try again or contact support if amount was debited.'
            })
    
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount format'})

# Admin Reports Route
@admin_bp.route("/reports")
@login_required(['admin'])
def admin_reports():
    """Admin Reports Dashboard"""
    generate_comprehensive_admin_data()
    
    # Calculate comprehensive statistics for reports
    stats = {
        'projects': {
            'total': len(admin_projects_data),
            'verified': len([p for p in admin_projects_data if p['status'] == 'Verified']),
            'pending': len([p for p in admin_projects_data if p['status'] == 'Pending Review']),
            'under_review': len([p for p in admin_projects_data if p['status'] == 'Under Verification']),
        },
        'ngos': {
            'total': len(admin_ngos_data),
            'verified': len([n for n in admin_ngos_data if n['status'] == 'Verified']),
            'pending': len([n for n in admin_ngos_data if n['status'] == 'Pending'])
        },
        'industries': {
            'total': len(admin_industries_data),
            'verified': len([i for i in admin_industries_data if i['status'] == 'Verified']),
            'pending': len([i for i in admin_industries_data if i['status'] == 'Pending'])
        },
        'credits': {
            'total_issued': sum(p['credits_approved'] for p in admin_projects_data if p['status'] == 'Verified'),
            'total_purchased': sum(i['credits_purchased'] for i in admin_industries_data),
            'total_revenue': sum(i['revenue_contributed'] for i in admin_industries_data)
        }
    }
    
    return render_template('admin/reports.html', stats=stats)

# Industry Registration System Routes
@industry_bp.route("/register", methods=['GET', 'POST'])
def industry_register():
    """Industry/Company Registration with Admin Approval"""
    if request.method == 'POST':
        try:
            # Extract form data
            company_name = request.form.get('company_name', '').strip()
            trading_name = request.form.get('trading_name', '').strip()
            industry_type = request.form.get('industry_type', '').strip()
            company_size = request.form.get('company_size', '').strip()
            business_description = request.form.get('business_description', '').strip()
            
            # Legal details
            cin = request.form.get('cin', '').strip()
            pan = request.form.get('pan', '').strip()
            gstin = request.form.get('gstin', '').strip()
            incorporation_date = request.form.get('incorporation_date', '')
            authorized_capital = request.form.get('authorized_capital', '')
            paid_up_capital = request.form.get('paid_up_capital', '')
            
            # Contact information
            registered_address = request.form.get('registered_address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            website = request.form.get('website', '').strip()
            primary_phone = request.form.get('primary_phone', '').strip()
            primary_email = request.form.get('primary_email', '').strip()
            
            # Key personnel
            signatory_name = request.form.get('signatory_name', '').strip()
            signatory_designation = request.form.get('signatory_designation', '').strip()
            signatory_email = request.form.get('signatory_email', '').strip()
            signatory_phone = request.form.get('signatory_phone', '').strip()
            env_officer_name = request.form.get('env_officer_name', '').strip()
            env_officer_email = request.form.get('env_officer_email', '').strip()
            
            # Environmental information
            annual_emissions = request.form.get('annual_emissions', '')
            emissions_scope = request.form.get('emissions_scope', '').strip()
            sustainability_initiatives = request.form.get('sustainability_initiatives', '').strip()
            carbon_interests = request.form.getlist('carbon_interests[]')
            
            # Validation
            required_fields = [
                company_name, industry_type, company_size, business_description,
                cin, pan, gstin, incorporation_date, authorized_capital, paid_up_capital,
                registered_address, city, state, pincode, primary_phone, primary_email,
                signatory_name, signatory_designation, signatory_email, signatory_phone,
                annual_emissions, emissions_scope
            ]
            
            if not all(required_fields):
                return jsonify({
                    'success': False,
                    'message': 'Please fill in all required fields.'
                })
            
            if len(carbon_interests) == 0:
                return jsonify({
                    'success': False,
                    'message': 'Please select at least one carbon credits interest.'
                })
            
            # Generate application ID
            application_id = f'APP{random.randint(100000, 999999)}'
            
            # Create industry application record
            new_application = {
                'id': application_id,
                'company_name': company_name,
                'trading_name': trading_name,
                'industry_type': industry_type,
                'company_size': company_size,
                'business_description': business_description,
                'cin': cin,
                'pan': pan,
                'gstin': gstin,
                'incorporation_date': incorporation_date,
                'authorized_capital': int(authorized_capital),
                'paid_up_capital': int(paid_up_capital),
                'registered_address': registered_address,
                'city': city,
                'state': state,
                'pincode': pincode,
                'website': website,
                'primary_phone': primary_phone,
                'primary_email': primary_email,
                'signatory_name': signatory_name,
                'signatory_designation': signatory_designation,
                'signatory_email': signatory_email,
                'signatory_phone': signatory_phone,
                'env_officer_name': env_officer_name,
                'env_officer_email': env_officer_email,
                'annual_emissions': float(annual_emissions),
                'emissions_scope': emissions_scope,
                'sustainability_initiatives': sustainability_initiatives,
                'carbon_interests': carbon_interests,
                'status': 'Pending',  # Requires admin approval
                'application_date': datetime.now(),
                'approval_date': None,
                'verification_notes': '',
                'documents_uploaded': [],  # In production, handle file uploads
                'contact_person': signatory_name,
                'phone': primary_phone,
                'email': primary_email,
                'address': registered_address,
                'sector': industry_type,
                'registration_number': f'IND/REG/{application_id}',
                'wallet_address': f'0x{random.randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999):040x}',
                'bank_name': '',  # Can be added later in admin approval
                'account_number': '',
                'credits_purchased': 0,
                'revenue_contributed': 0,
                'registration_date': datetime.now(),
                'verification_date': None,
                'purchase_history': []
            }
            
            # Add to admin industries data for review
            admin_industries_data.append(new_application)
            
            # Send registration confirmation email
            try:
                email_system.send_industry_registration_confirmation(
                    email=primary_email,
                    contact_person=signatory_name,
                    company_name=company_name
                )
                logger.info(f"Industry registration confirmation email sent to {primary_email}")
            except Exception as e:
                logger.error(f"Failed to send industry registration confirmation email: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Registration submitted successfully! Your application will be reviewed within 3-5 business days. Check your email for confirmation.',
                'application_id': application_id
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            })
    
    return render_template('industry/register.html')

@industry_bp.route("/registration-success")
def registration_success():
    """Registration Success Page"""
    application_id = request.args.get('id', 'Unknown')
    return render_template('industry/registration_success.html', application_id=application_id)

@app.route('/projects/<project_id>/drone-analysis')
def get_drone_analysis(project_id):
    """Get comprehensive drone analysis report for a project"""
    generate_comprehensive_admin_data()
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'})
    
    # Get project coordinates
    if project.get('location'):
        coords = [float(c) for c in project['location'].split(',')]
    else:
        coords = [19.0760, 72.8777]  # Default Mumbai coordinates
    
    # Generate comprehensive drone analysis report
    drone_report = drone_processor.get_comprehensive_drone_report(
        project_id=project_id,
        coordinates=coords
    )
    
    return jsonify(drone_report)

@app.route('/projects/<project_id>/geospatial-analysis')
def get_geospatial_analysis(project_id):
    """Get comprehensive geospatial GIS analysis for a project"""
    generate_comprehensive_admin_data()
    
    project = next((p for p in admin_projects_data if p['id'] == project_id), None)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'})
    
    # Convert project data to format expected by geospatial analyzer
    project_data = {
        'id': project['id'],
        'name': project['name'],
        'location': project.get('location', '19.0760,72.8777'),
        'area_hectares': project.get('area', 10),  # Default 10 hectares
        'ecosystem': project.get('ecosystem', 'mangrove')
    }
    
    # Generate comprehensive GIS analysis report
    gis_report = geospatial_analyzer.generate_comprehensive_gis_report(project_data)
    
    return jsonify(gis_report)

@app.route('/blockchain/token-visualization')
def get_token_visualization():
    """Get blockchain token flow visualization data"""
    project_id = request.args.get('project_id')
    timeframe_days = int(request.args.get('timeframe_days', 365))
    
    # Generate token flow visualization
    visualization_data = token_viz_engine.generate_token_flow_visualization(
        project_id=project_id,
        timeframe_days=timeframe_days
    )
    
    return jsonify(visualization_data)

@app.route('/blockchain/live-dashboard')
def get_live_token_dashboard():
    """Get real-time blockchain token dashboard data"""
    project_id = request.args.get('project_id')
    
    # Generate real-time dashboard data
    dashboard_data = token_viz_engine.create_real_time_dashboard_data(project_id=project_id)
    
    return jsonify(dashboard_data)


# Debug API endpoint for real-time project monitoring
@app.route('/api/debug/projects-state')
def debug_projects_state():
    """Debug endpoint to check current projects state"""
    generate_comprehensive_admin_data()
    
    pending_projects = [p for p in admin_projects_data if p['status'] in ['Pending Review', 'Documents Missing', 'Under Verification']]
    verified_projects = [p for p in admin_projects_data if p['status'] == 'Verified']
    
    # Get recent projects (last 10)
    recent_projects = sorted(admin_projects_data, key=lambda x: x.get('submission_date', datetime.now()), reverse=True)[:10]
    
    return jsonify({
        'total_projects': len(admin_projects_data),
        'pending_projects': len(pending_projects),
        'verified_projects': len(verified_projects),
        'recent_projects': [{
            'id': p['id'],
            'name': p['name'],
            'ngo_name': p['ngo_name'],
            'status': p['status'],
            'submission_date': p['submission_date'].isoformat() if isinstance(p['submission_date'], datetime) else str(p['submission_date'])
        } for p in recent_projects],
        'all_statuses': list(set(p['status'] for p in admin_projects_data))
    })

# Location Management API endpoints
@app.route('/api/location/validate', methods=['POST'])
def validate_location_api():
    """API endpoint to validate coordinates for coastal suitability"""
    try:
        data = request.json
        lat = float(data.get('latitude'))
        lng = float(data.get('longitude'))
        
        validation_result = location_manager.validate_coordinates(lat, lng)
        return jsonify({
            'success': True,
            'validation': validation_result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/location/geocode', methods=['POST'])
def geocode_location_api():
    """API endpoint to convert location name to coordinates"""
    try:
        data = request.json
        location_name = data.get('location')
        
        result = location_manager.geocode_location(location_name)
        
        if result:
            return jsonify({
                'success': True,
                'location': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Location not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/location/reverse-geocode', methods=['POST'])
def reverse_geocode_api():
    """API endpoint to convert coordinates to location information"""
    try:
        data = request.json
        lat = float(data.get('latitude'))
        lng = float(data.get('longitude'))
        
        result = location_manager.reverse_geocode(lat, lng)
        
        if result:
            return jsonify({
                'success': True,
                'location': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Location information not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/location/suitable-areas', methods=['POST'])
def get_suitable_areas_api():
    """API endpoint to find suitable locations for specific ecosystem types"""
    try:
        data = request.json
        ecosystem_type = data.get('ecosystem_type')
        area_required = data.get('area_required')
        
        suitable_locations = location_manager.find_suitable_locations(ecosystem_type, area_required)
        
        return jsonify({
            'success': True,
            'suitable_locations': suitable_locations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/location/area-calculation', methods=['POST'])
def calculate_area_api():
    """API endpoint to calculate area from polygon coordinates"""
    try:
        data = request.json
        coordinates = data.get('coordinates')  # Array of [lat, lng] pairs
        
        # Convert to tuples for calculation
        coord_tuples = [(coord[0], coord[1]) for coord in coordinates]
        area = location_manager.calculate_area_from_coordinates(coord_tuples)
        
        return jsonify({
            'success': True,
            'area_hectares': area,
            'area_acres': area * 2.47105  # Convert hectares to acres
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/location/project-recommendations', methods=['POST'])
def get_project_recommendations_api():
    """API endpoint to get comprehensive project location recommendations"""
    try:
        data = request.json
        
        recommendations = location_manager.get_project_location_recommendations(data)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Carbon Calculation API Routes
@app.route('/api/carbon/calculate', methods=['POST'])
def calculate_carbon_api():
    """API endpoint to calculate carbon sequestration for projects"""
    try:
        data = request.json
        
        # Extract project parameters
        tree_species = data.get('tree_species', 'Mangrove')
        number_of_trees = int(data.get('number_of_trees', 0))
        tree_height = float(data.get('tree_height', 2.0))
        tree_age = int(data.get('tree_age', 1))
        area_hectares = float(data.get('area', 10.0))
        
        # Validate inputs
        if number_of_trees <= 0:
            return jsonify({
                'success': False,
                'error': 'Number of trees must be greater than 0'
            }), 400
        
        # Calculate carbon using ML predictions
        project_data = {
            'tree_species': tree_species,
            'number_of_trees': number_of_trees,
            'tree_height': tree_height,
            'tree_age': tree_age,
            'area': area_hectares,
            'location': '19.0760,72.8777'  # Default Mumbai coordinates
        }
        
        # Get carbon sequestration prediction
        prediction = ml_predictor.predict_carbon_sequestration(project_data, forecast_years=20)
        
        # Extract current year carbon storage
        current_carbon = 0
        if prediction.get('predictions', {}).get('annual_forecast'):
            current_carbon = prediction['predictions']['annual_forecast'][0].get('cumulative_co2', 0)
        
        # Calculate additional metrics
        carbon_per_tree = current_carbon / number_of_trees if number_of_trees > 0 else 0
        carbon_per_hectare = current_carbon / area_hectares if area_hectares > 0 else 0
        
        return jsonify({
            'success': True,
            'carbon_stored_tonnes': round(current_carbon, 2),
            'carbon_per_tree': round(carbon_per_tree, 4),
            'carbon_per_hectare': round(carbon_per_hectare, 2),
            'project_parameters': project_data,
            '20_year_forecast': prediction.get('predictions', {}).get('summary', {}),
            'calculation_date': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-plant-species', methods=['POST'])
def analyze_plant_species_api():
    """API endpoint for plant species detection from images"""
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No image file provided'
        }), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No image selected'
        }), 400
    
    try:
        # Read image data
        image_data = image_file.read()
        image_file.seek(0)
        
        # Convert to base64 for analysis
        import base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # Detect plants in the image
        is_plant, validation_result = detect_plant_in_image(encoded_image)
        
        if not is_plant:
            return jsonify({
                'success': False,
                'error': 'No plants detected in the image',
                'confidence': 0,
                'species': None
            })
        
        # Analyze species based on plant characteristics
        confidence_score = validation_result.get('confidence', 75) if isinstance(validation_result, dict) else 75
        plant_percentage = validation_result.get('plant_percentage', 20) if isinstance(validation_result, dict) else 20
        
        # Determine species based on plant characteristics
        if plant_percentage > 30:
            species = random.choice(['Rhizophora mangle', 'Avicennia marina', 'Mangrove Forest'])
        elif plant_percentage > 20:
            species = random.choice(['Coastal Vegetation', 'Mangrove Sapling', 'Marine Pine'])
        else:
            species = random.choice(['Young Sapling', 'Coastal Shrub', 'Small Tree'])
        
        return jsonify({
            'success': True,
            'species': species,
            'confidence': confidence_score / 100,
            'plant_coverage_percentage': plant_percentage,
            'analysis_method': 'Computer Vision + Color Analysis',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Species analysis error: {str(e)}'
        }), 500

# MRV Workflow API Routes
@app.route('/api/mrv/workflows', methods=['GET'])
@login_required(['admin'])
def get_mrv_workflows():
    """Get all MRV workflows with filtering"""
    try:
        project_id = request.args.get('project_id')
        status = request.args.get('status')
        stage = request.args.get('stage')
        
        workflows = []
        for workflow_id, workflow in mrv_workflow_engine.workflows.items():
            workflow_status = mrv_workflow_engine.get_workflow_status(workflow_id)
            if workflow_status:
                # Apply filters
                if project_id and workflow_status['project_id'] != project_id:
                    continue
                if status and workflow_status['status'] != status:
                    continue
                if stage and workflow_status['current_stage'] != stage:
                    continue
                workflows.append(workflow_status)
        
        return jsonify({
            'success': True,
            'data': {
                'workflows': workflows,
                'total_count': len(workflows)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mrv/workflows/<workflow_id>', methods=['GET'])
@login_required(['admin', 'ngo'])
def get_mrv_workflow_details(workflow_id):
    """Get detailed MRV workflow information"""
    try:
        workflow_status = mrv_workflow_engine.get_workflow_status(workflow_id)
        if not workflow_status:
            return jsonify({
                'success': False,
                'error': 'Workflow not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': workflow_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mrv/verification/<project_id>', methods=['GET'])
@login_required(['admin', 'ngo'])
def get_project_verification_results(project_id):
    """Get automated verification results for a project"""
    try:
        # Find project in admin data
        project = next((p for p in admin_projects_data if p['id'] == project_id), None)
        if not project:
            return jsonify({
                'success': False,
                'error': 'Project not found'
            }), 404
        
        # Run verification if not already done
        import asyncio
        verification_results = asyncio.run(mrv_workflow_engine.verification_engine.verify_project(project))
        
        results_data = []
        for result in verification_results:
            results_data.append({
                'criteria': result.criteria.value,
                'passed': result.passed,
                'score': result.score,
                'confidence': result.confidence,
                'details': result.details,
                'evidence': result.evidence,
                'timestamp': result.timestamp.isoformat(),
                'validator_id': result.validator_id
            })
        
        overall_score = sum(r.score for r in verification_results) / len(verification_results)
        
        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'overall_score': overall_score,
                'verification_results': results_data,
                'total_criteria': len(verification_results),
                'passed_criteria': len([r for r in verification_results if r.passed])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Real Satellite Data API Routes
@app.route('/api/satellite/monitoring-data', methods=['POST'])
def get_satellite_monitoring_data():
    """Get comprehensive satellite monitoring data for a location"""
    try:
        data = request.get_json()
        coordinates = (data.get('latitude'), data.get('longitude'))
        date_range = (data.get('start_date'), data.get('end_date'))
        area_km2 = data.get('area_km2', 1.0)
        
        if not all(coordinates) or not all(date_range):
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
        
        # Get comprehensive monitoring data
        monitoring_data = real_satellite_integration.get_comprehensive_monitoring_data(
            coordinates, date_range, area_km2
        )
        
        return jsonify({
            'success': True,
            'data': monitoring_data
        })
        
    except Exception as e:
        logger.error(f"Satellite monitoring data error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/satellite/ndvi-analysis', methods=['POST'])
def get_ndvi_analysis():
    """Get NDVI analysis for vegetation health assessment"""
    try:
        data = request.get_json()
        coordinates = (data.get('latitude'), data.get('longitude'))
        date_range = (data.get('start_date'), data.get('end_date'))
        area_km2 = data.get('area_km2', 1.0)
        
        if not all(coordinates) or not all(date_range):
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
        
        # Get NDVI data from Google Earth Engine
        ndvi_data = real_satellite_integration.gee_api.get_ndvi_data(
            coordinates, date_range, area_km2
        )
        
        return jsonify({
            'success': True,
            'data': ndvi_data
        })
        
    except Exception as e:
        logger.error(f"NDVI analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drone/process-imagery', methods=['POST'])
def process_drone_imagery():
    """Process drone imagery for vegetation analysis"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        gps_coordinates = (float(request.form.get('latitude')), float(request.form.get('longitude')))
        altitude_m = float(request.form.get('altitude_m', 100))
        sensor_type = request.form.get('sensor_type', 'rgb')
        
        # Save uploaded image temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image_file.save(tmp_file.name)
            
            # Process the image
            result = real_satellite_integration.drone_processor.process_drone_imagery(
                tmp_file.name, gps_coordinates, altitude_m, sensor_type
            )
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Drone imagery processing error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/satellite/ecosystem-health', methods=['POST'])
def get_ecosystem_health():
    """Get comprehensive ecosystem health assessment"""
    try:
        data = request.get_json()
        coordinates = (data.get('latitude'), data.get('longitude'))
        date_range = (data.get('start_date'), data.get('end_date'))
        area_km2 = data.get('area_km2', 1.0)
        
        if not all(coordinates) or not all(date_range):
            return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
        
        # Get comprehensive monitoring data
        monitoring_data = real_satellite_integration.get_comprehensive_monitoring_data(
            coordinates, date_range, area_km2
        )
        
        # Extract ecosystem health information
        ecosystem_health = monitoring_data.get('ecosystem_health', {})
        
        return jsonify({
            'success': True,
            'data': {
                'coordinates': coordinates,
                'ecosystem_health': ecosystem_health,
                'monitoring_summary': {
                    'ndvi_status': monitoring_data['data_sources'].get('ndvi', {}).get('success', False),
                    'imagery_status': monitoring_data['data_sources'].get('high_res_imagery', {}).get('success', False),
                    'landsat_status': monitoring_data['data_sources'].get('landsat', {}).get('success', False)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Ecosystem health assessment error: {e}")
# Push Notification API Routes
@app.route('/api/notifications/subscribe', methods=['POST'])
def subscribe_to_notifications():
    """Subscribe user to push notifications"""
    try:
        data = request.get_json()
        subscription = data.get('subscription')
        user_id = data.get('user_id')
        user_role = data.get('user_role')
        
        if not subscription or not user_id:
            return jsonify({'success': False, 'error': 'Missing subscription data'}), 400
        
        # Store subscription in database (in production)
        # For now, just return success
        logger.info(f"User {user_id} ({user_role}) subscribed to notifications")
        
        return jsonify({
            'success': True,
            'message': 'Successfully subscribed to notifications'
        })
        
    except Exception as e:
        logger.error(f"Notification subscription error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send push notification to users"""
    try:
        data = request.get_json()
        title = data.get('title', 'BlueCarbon MRV')
        body = data.get('body', 'New update available')
        url = data.get('url', '/')
        user_role = data.get('user_role', 'all')
        
        # In production, this would send actual push notifications
        # For now, just log the notification
        logger.info(f"Notification sent: {title} - {body} (Role: {user_role})")
        
        return jsonify({
            'success': True,
            'message': 'Notification sent successfully'
        })
        
    except Exception as e:
        logger.error(f"Send notification error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Health and Diagnostic API Routes
@app.route('/api/health/integrations', methods=['GET'])
def health_check_integrations():
    """Health check for all external integrations (read-only)"""
    try:
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'operational',
            'integrations': {}
        }
        
        # Check Firebase integration
        firebase_config = get_integration_config('firebase')
        health_status['integrations']['firebase'] = {
            'status': 'enabled' if firebase_config.get('enabled') else 'disabled',
            'mode': 'mock' if firebase_config.get('mock_mode') else 'production',
            'features': ['authentication', 'realtime_database', 'cloud_functions']
        }
        
        # Check Supabase integration
        supabase_enabled = is_feature_enabled('firebase')  # Using same flag for now
        health_status['integrations']['supabase'] = {
            'status': 'enabled' if supabase_enabled else 'disabled',
            'mode': 'mock' if not supabase_enabled else 'production',
            'features': ['database', 'realtime', 'auth']
        }
        
        # Check Satellite integration
        satellite_config = get_integration_config('satellite')
        health_status['integrations']['satellite'] = {
            'status': 'enabled' if satellite_config.get('enabled') else 'disabled',
            'mode': 'mock' if satellite_config.get('mock_mode') else 'production',
            'providers': {
                'google_earth_engine': bool(satellite_config.get('google_earth_engine_key')),
                'planet_labs': bool(satellite_config.get('planet_labs_key')),
                'nasa': bool(satellite_config.get('nasa_key'))
            }
        }
        
        # Check Drone integration
        drone_config = get_integration_config('drone')
        health_status['integrations']['drone'] = {
            'status': 'enabled' if drone_config.get('enabled') else 'disabled',
            'processing_enabled': drone_config.get('processing_enabled', True),
            'features': ['imagery_analysis', 'lidar_processing', '3d_mapping']
        }
        
        # Check Email integration
        email_config = get_integration_config('email')
        health_status['integrations']['email'] = {
            'status': 'enabled' if email_config.get('enabled') else 'disabled',
            'smtp_configured': bool(email_config.get('smtp_server')),
            'features': ['notifications', 'verification_emails', 'alerts']
        }
        
        # Check Blockchain integration
        blockchain_config = get_integration_config('blockchain')
        health_status['integrations']['blockchain'] = {
            'status': 'enabled' if blockchain_config.get('enabled') else 'disabled',
            'mode': 'simulation',  # Currently always simulation
            'network': blockchain_config.get('network', 'testnet'),
            'features': ['token_minting', 'transfers', 'smart_contracts']
        }
        
        # Check PWA features
        pwa_config = get_integration_config('pwa')
        health_status['integrations']['pwa'] = {
            'status': 'enabled' if pwa_config.get('enabled') else 'disabled',
            'push_notifications': pwa_config.get('push_notifications', False),
            'background_sync': pwa_config.get('background_sync', True),
            'features': ['offline_support', 'app_installation', 'service_worker']
        }
        
        # Overall system health
        enabled_count = sum(1 for integration in health_status['integrations'].values() 
                          if integration['status'] == 'enabled')
        total_count = len(health_status['integrations'])
        health_percentage = (enabled_count / total_count) * 100
        
        if health_percentage >= 80:
            health_status['system_status'] = 'healthy'
        elif health_percentage >= 60:
            health_status['system_status'] = 'degraded'
        else:
            health_status['system_status'] = 'critical'
        
        health_status['summary'] = {
            'enabled_integrations': enabled_count,
            'total_integrations': total_count,
            'health_percentage': round(health_percentage, 1)
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'system_status': 'error',
            'error': str(e),
            'integrations': {}
        }), 500

@app.route('/api/health/system', methods=['GET'])
def health_check_system():
    """Basic system health check"""
    try:
        # Get system metrics
        metrics = get_metrics()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': production_config['environment'],
            'database': {
                'status': 'connected',
                'type': production_database['type']
            },
            'features': {
                'blockchain': True,
                'satellite_monitoring': True,
                'drone_processing': True,
                'ml_predictions': True,
                'pwa_support': True
            },
            'metrics': {
                'total_metrics': len(metrics),
                'last_updated': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"System health check error: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# Test route for responsive design (development only)
@app.route('/test/responsive')
def responsive_test():
    """Test page for responsive design validation"""
    return render_template('responsive_test.html', 
                         title='Responsive Design Test',
                         header='📱 Responsive Design Test',
                         active='test')

# Register blueprints at import time for production deployment
app.register_blueprint(admin_bp)
app.register_blueprint(ngo_bp)
app.register_blueprint(industry_bp)
app.register_blueprint(blockchain_bp)  # Add blockchain API routes (simulation)
app.register_blueprint(real_blockchain_bp)  # Add real blockchain API routes
app.register_blueprint(research_bp)  # Add research dashboard

if __name__ == "__main__":
    # Print startup information
    print("\n" + "="*60)
    print("🌊 BlueCarbon MRV System Starting Up")
    print("="*60)
    print(f"Flask Environment: {os.environ.get('FLASK_ENV', 'production')}")
    print(f"Debug Mode: {app.debug}")
    print(f"Production Mode: {is_production()}")
    print(f"Firebase Mode: {'Production' if external_apis['firebase']['enabled'] else 'Mock Mode'}")
    print(f"Database Mode: {'Production' if is_production() else 'Development'}")
    
    # Get port from environment or default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    
    # Use production settings if not in development
    if is_production():
        host = '0.0.0.0'
        debug_mode = False
        print(f"Production Server: Running on port {port}")
    else:
        host = '127.0.0.1'
        debug_mode = True
        print(f"Development Server: http://127.0.0.1:{port}")
    
    print("\n🔗 Available API Endpoints:")
    print("   • /api/blockchain/stats - Blockchain statistics")
    print("   • /api/blockchain/tokens - Token management")
    print("   • /api/blockchain/transactions - Transaction history")
    print("   • /api/blockchain/visualization/* - Data visualization")
    print("   • /api/mrv/workflows - MRV workflow management")
    print("   • /api/mrv/verification/* - Automated verification results")
    print("   • /api/satellite/monitoring-data - Real satellite monitoring")
    print("   • /api/satellite/ndvi-analysis - NDVI vegetation analysis")
    print("   • /api/satellite/ecosystem-health - Ecosystem health assessment")
    print("   • /api/drone/process-imagery - Drone imagery processing")
    print("   • /api/location/validate - Validate coordinates")
    print("   • /api/location/geocode - Location name to coordinates")
    print("   • /api/location/reverse-geocode - Coordinates to location")
    print("   • /api/location/suitable-areas - Find suitable ecosystem areas")
    print("   • /api/location/area-calculation - Calculate polygon area")
    print("   • /api/location/project-recommendations - Location recommendations")
    
    if not is_production():
        print(f"\n📊 Admin Dashboard: http://127.0.0.1:{port}/admin/login")
        print(f"🏢 Industry Portal: http://127.0.0.1:{port}/industry/login")
        print(f"🌱 NGO Dashboard: http://127.0.0.1:{port}/ngo/dashboard")
    
    print("\n⚠️  Remember to set up .env file for production!")
    print("="*60 + "\n")
    
    app.run(debug=debug_mode, host=host, port=port)
