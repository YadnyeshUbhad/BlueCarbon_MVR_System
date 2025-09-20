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

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

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
            status = random.choice(['Verified', 'Pending', 'Blacklisted'])
            projects_count = len([p for p in admin_projects_data if p['ngo_name'] == name])
            credits_earned = sum(p['credits_approved'] for p in admin_projects_data if p['ngo_name'] == name)
            
            ngo = {
                'id': f'NGO{2000 + i}',
                'name': name,
                'registration_number': f'NGO/REG/2020/{1000 + i}',
                'status': status,
                'contact_person': f'Director {i+1}',
                'phone': f'+91-{random.randint(7000000000, 9999999999)}',
                'email': f'contact@{name.lower().replace(" ", "")}.org',
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
            status = random.choice(['Verified', 'Pending'])
            credits_purchased = random.randint(100, 2000)
            price_per_credit = random.randint(180, 280)
            revenue_contributed = credits_purchased * price_per_credit
            
            industry = {
                'id': f'IND{3000 + i}',
                'name': name,
                'sector': random.choice(sectors),
                'registration_number': f'IND/REG/{random.randint(100000, 999999)}',
                'status': status,
                'contact_person': f'Manager {i+1}',
                'phone': f'+91-{random.randint(7000000000, 9999999999)}',
                'email': f'contact@{name.lower().replace(" ", "").replace("ltd", "").replace("corp", "").replace("inc", "")}',
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

# NGO blueprint
ngo_bp = Blueprint("ngo", __name__, url_prefix="/ngo")

@ngo_bp.route("/dashboard")
def ngo_dashboard():
    """NGO Dashboard - Main landing page for NGOs"""
    generate_comprehensive_admin_data()
    
    # Get sample NGO data (in production, this would be based on logged-in NGO)
    ngo = admin_ngos_data[0] if admin_ngos_data else {
        'name': 'Demo NGO',
        'credits_earned': 0,
        'projects_submitted': 0,
        'total_revenue': 0
    }
    
    # Get NGO's projects
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    approved_projects = [p for p in ngo_projects if p['status'] == 'Verified']
    pending_projects = [p for p in ngo_projects if p['status'] in ['Pending Review', 'Under Verification', 'Documents Missing']]
    
    # Calculate stats that match the template
    stats = {
        'total_projects': len(ngo_projects),
        'approved_projects': len(approved_projects),
        'credits_earned': sum(p['credits_approved'] for p in approved_projects),
        'pending_verifications': len(pending_projects),
        'reversed_applications': len([p for p in ngo_projects if p['status'] == 'Rejected']),
        'revenue_generated': sum(t['total_value'] for t in transactions_data if any(p['name'] == t['project_name'] and p['ngo_name'] == ngo['name'] for p in ngo_projects) and t['status'] == 'Completed'),
        'projects_change': 15,  # Mock data
        'approved_change': 85,  # Mock data
        'credits_change': 25,   # Mock data
        'avg_verification_time': 12,  # Mock data
        'reversed_change': 5,   # Mock data
        'revenue_change': 40    # Mock data
    }
    
    # Recent activities (mock data)
    recent_activities = [
        {'title': 'Project "Sundarbans Restoration" approved', 'time': '2 hours ago', 'type': 'success'},
        {'title': 'New project submission received', 'time': '1 day ago', 'type': 'info'},
        {'title': 'Credits transferred to marketplace', 'time': '2 days ago', 'type': 'warning'},
        {'title': 'Profile updated successfully', 'time': '3 days ago', 'type': 'primary'}
    ]
    
    return render_template('ngo/dashboard.html', ngo=ngo, stats=stats, projects=ngo_projects[:5], recent_activities=recent_activities, active='dashboard')

@ngo_bp.route("/profile")
def ngo_profile():
    """NGO Profile Page"""
    generate_comprehensive_admin_data()
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    
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

@ngo_bp.route("/projects")
def ngo_projects():
    """NGO Projects Page - Shows all projects submitted by the NGO"""
    generate_comprehensive_admin_data()
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    return render_template('ngo/projects.html', projects=ngo_projects, ngo=ngo, active='projects')

@ngo_bp.route("/projects/new", methods=['GET', 'POST'])
def ngo_projects_new():
    """New Project Registration"""
    if request.method == 'POST':
        return submit_project()
    return render_template('ngo/project_new.html', active='new_project')

@ngo_bp.route("/projects/submit", methods=['POST'])
def submit_project():
    """Handle project submission and add to admin database"""
    try:
        # Generate comprehensive admin data to ensure the lists are initialized
        generate_comprehensive_admin_data()
        
        # Get current NGO (in production, this would come from session)
        ngo_name = admin_ngos_data[0]['name'] if admin_ngos_data else 'Demo NGO'
        ngo_id = admin_ngos_data[0]['id'] if admin_ngos_data else 'NGO2000'
        
        # Generate new project ID
        project_id = f'PROJ{1000 + len(admin_projects_data) + 1}'
        
        # Extract form data
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
            'location': request.form.get('location', ''),
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
            'phone': admin_ngos_data[0]['phone'] if admin_ngos_data else '+91-9876543210',
            'email': admin_ngos_data[0]['email'] if admin_ngos_data else 'contact@ngo.org',
            'documents': ['Project Proposal', 'Environmental Assessment'],
            # New fields for location parsing
            'state': 'Maharashtra',  # Default, could be extracted from location
            'district': request.form.get('admin_area', '').split(',')[0] if request.form.get('admin_area') else 'Mumbai'
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
        
        flash(f'Project "{project_data["name"]}" submitted successfully! Project ID: {project_id}', 'success')
        return redirect(url_for('ngo.ngo_dashboard'))
        
    except Exception as e:
        flash(f'Error submitting project: {str(e)}', 'error')
        return redirect(url_for('ngo.ngo_projects_new'))

@ngo_bp.route("/credits")
def ngo_credits():
    """NGO Credits Page - Shows all credits earned"""
    generate_comprehensive_admin_data()
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    approved_projects = [p for p in ngo_projects if p['status'] == 'Verified']
    
    # Create credits data with proper format
    credits_data = []
    total_revenue = 0
    for project in approved_projects:
        revenue = project['credits_approved'] * random.randint(180, 250)
        total_revenue += revenue
        credits_data.append({
            'project': project['name'],
            'vintage': project['approval_date'].year if project['approval_date'] else 2024,
            'amount': project['credits_approved'],
            'verification': 'Verified',
            'token': project['token_id'],
            'status': random.choice(['Available', 'Sold']),
            'revenue': revenue
        })
    
    # Calculate stats
    total_credits = sum(p['credits_approved'] for p in approved_projects)
    verified_credits = total_credits  # All approved projects are verified
    pending_credits = sum(p['credits_requested'] for p in ngo_projects if p['status'] in ['Pending Review', 'Under Verification'])
    sold_credits = sum(c['amount'] for c in credits_data if c['status'] == 'Sold')
    
    stats = {
        'total_credits': total_credits,
        'verified_credits': verified_credits,
        'pending_credits': pending_credits,
        'sold_credits': sold_credits,
        'total_revenue': total_revenue
    }
    
    return render_template('ngo/credits.html', credits=credits_data, stats=stats, active='credits')

@ngo_bp.route("/revenue")
def ngo_revenue():
    """NGO Revenue Page - Shows revenue from credit sales"""
    generate_comprehensive_admin_data()
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    
    # Get transactions for this NGO's projects
    ngo_transactions = [t for t in transactions_data if any(p['name'] == t['project_name'] and p['ngo_name'] == ngo['name'] for p in ngo_projects)]
    completed_transactions = [t for t in ngo_transactions if t['status'] == 'Completed']
    pending_transactions = [t for t in ngo_transactions if t['status'] in ['Pending', 'Processing']]
    
    # Calculate summary statistics
    total_revenue = sum(t['total_value'] for t in completed_transactions)
    pending_transfer = sum(t['total_value'] for t in pending_transactions)
    distributed = total_revenue  # Assuming distributed = completed revenue
    credits_sold = sum(t['credits_sold'] for t in completed_transactions) if completed_transactions else 0
    avg_price = round(total_revenue / credits_sold, 2) if credits_sold > 0 else 0
    
    # Create summary object for template
    summary = {
        'total_revenue': total_revenue,
        'pending_transfer': pending_transfer,
        'distributed': distributed,
        'credits_sold': credits_sold,
        'avg_price': avg_price
    }
    
    # Transform transactions for template (adjust field names)
    formatted_transactions = []
    for t in ngo_transactions:
        formatted_transactions.append({
            'id': t['id'],
            'project': t['project_name'],
            'credits': t['credits_sold'],
            'price': t['price_per_credit'],
            'total': t['total_value'],
            'buyer': t['buyer_name'],
            'date': t['transaction_date'],
            'status': t['status']
        })
    
    return render_template('ngo/revenue.html', transactions=formatted_transactions, total_revenue=total_revenue, summary=summary, active='revenue')

@ngo_bp.route("/upload/tree_data", methods=['POST'])
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
def credits_realtime():
    """Real-time credits data for live updates"""
    generate_comprehensive_admin_data()
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    
    # Mock real-time credits data
    credits_data = []
    for project in ngo_projects:
        if project['status'] == 'Verified':
            credits_data.append({
                'project': project['name'],
                'vintage': project['approval_date'].year if project['approval_date'] else 2024,
                'amount': project['credits_approved'],
                'verification': 'Verified',
                'token': project['token_id'],
                'status': random.choice(['Available', 'Sold']),
                'revenue': project['credits_approved'] * random.randint(180, 250)
            })
    
    return jsonify({
        'success': True,
        'total_credits': sum(c['amount'] for c in credits_data),
        'latest_credits': credits_data
    })

@ngo_bp.route("/revenue/realtime")
def revenue_realtime():
    """Real-time revenue data for live updates"""
    generate_comprehensive_admin_data()
    ngo = admin_ngos_data[0] if admin_ngos_data else {'name': 'Demo NGO'}
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    ngo_transactions = [t for t in transactions_data if any(p['name'] == t['project_name'] and p['ngo_name'] == ngo['name'] for p in ngo_projects)]
    
    total_revenue = sum(t['total_value'] for t in ngo_transactions if t['status'] == 'Completed')
    
    # Mock recent transactions
    recent_transactions = []
    for t in ngo_transactions[-3:]:  # Last 3 transactions
        recent_transactions.append({
            'project': t['project_name'],
            'total': t['total_value'],
            'buyer': t['buyer_name'],
            'status': t['status']
        })
    
    return jsonify({
        'success': True,
        'total_revenue': total_revenue,
        'recent_transactions': recent_transactions
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

@admin_bp.route("/login")
def admin_login():
    """NCCR Admin Login - redirect to main admin dashboard"""
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route("/")
def admin_dashboard():
    """NCCR Admin Dashboard - Overview with comprehensive statistics"""
    generate_comprehensive_admin_data()
    
    # Calculate comprehensive statistics
    total_projects = len(admin_projects_data)
    pending_verification = len([p for p in admin_projects_data if p['status'] in ['Pending Review', 'Documents Missing', 'Under Verification']])
    verified_projects = len([p for p in admin_projects_data if p['status'] == 'Verified'])
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
    
    return render_template('admin/dashboard.html', stats=stats, activities=activities, now=datetime.now())

@admin_bp.route("/projects")
def projects_management():
    """Projects Management - Main page with pending and verified tabs"""
    generate_comprehensive_admin_data()
    
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
        project['token_id'] = f'BC{random.randint(100000, 999999)}'
        project['credits_approved'] = approved_credits
        project['verification_notes'] = f'Approved: {reason}' if reason else 'Approved'
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

@admin_bp.route("/ngos")
def ngos_management():
    """NGO Management Dashboard"""
    generate_comprehensive_admin_data()
    
    # Filter NGOs
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    filtered_ngos = admin_ngos_data.copy()
    if status_filter:
        filtered_ngos = [n for n in filtered_ngos if n['status'] == status_filter]
    if search:
        filtered_ngos = [n for n in filtered_ngos if 
                        search.lower() in n['name'].lower() or 
                        search.lower() in n['contact_person'].lower() or
                        search in n['id']]
    
    # Sort by credits earned (ranking)
    sort_by = request.args.get('sort', 'credits_earned')
    if sort_by == 'credits_earned':
        filtered_ngos.sort(key=lambda x: x['credits_earned'], reverse=True)
    elif sort_by == 'revenue':
        filtered_ngos.sort(key=lambda x: x['total_revenue'], reverse=True)
    elif sort_by == 'projects':
        filtered_ngos.sort(key=lambda x: x['projects_submitted'], reverse=True)
    
    # NGO statistics
    ngo_stats = {
        'total': len(admin_ngos_data),
        'verified': len([n for n in admin_ngos_data if n['status'] == 'Verified']),
        'pending': len([n for n in admin_ngos_data if n['status'] == 'Pending']),
        'blacklisted': len([n for n in admin_ngos_data if n['status'] == 'Blacklisted'])
    }
    
    return render_template('admin/ngos.html',
                         ngos=filtered_ngos,
                         stats=ngo_stats,
                         status_filter=status_filter,
                         search=search,
                         sort_by=sort_by)

@admin_bp.route("/ngos/<ngo_id>")
def ngo_details(ngo_id):
    """Detailed view of a specific NGO"""
    generate_comprehensive_admin_data()
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        flash('NGO not found', 'error')
        return redirect(url_for('admin.ngos_management'))
    
    # Get NGO's projects
    ngo_projects = [p for p in admin_projects_data if p['ngo_name'] == ngo['name']]
    
    return render_template('admin/ngo_details.html', ngo=ngo, projects=ngo_projects)

@admin_bp.route("/ngos/<ngo_id>/action", methods=['POST'])
def ngo_action(ngo_id):
    """Handle NGO actions (verify, blacklist, edit)"""
    generate_comprehensive_admin_data()
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    ngo = next((n for n in admin_ngos_data if n['id'] == ngo_id), None)
    if not ngo:
        return jsonify({'success': False, 'message': 'NGO not found'})
    
    if action == 'verify':
        ngo['status'] = 'Verified'
        ngo['verification_date'] = datetime.now()
        message = f'NGO {ngo["name"]} verified successfully'
        
    elif action == 'blacklist':
        ngo['status'] = 'Blacklisted'
        ngo['blacklist_reason'] = reason
        message = f'NGO {ngo["name"]} blacklisted successfully'
        
    elif action == 'edit':
        # Handle edit form data
        ngo['contact_person'] = request.form.get('contact_person', ngo['contact_person'])
        ngo['phone'] = request.form.get('phone', ngo['phone'])
        ngo['email'] = request.form.get('email', ngo['email'])
        message = f'NGO {ngo["name"]} information updated successfully'
    
    return jsonify({'success': True, 'message': message})

@admin_bp.route("/industries")
def industries_management():
    """Industries Management Dashboard"""
    generate_comprehensive_admin_data()
    
    # Filter Industries
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    sector_filter = request.args.get('sector', '')
    
    filtered_industries = admin_industries_data.copy()
    if status_filter:
        filtered_industries = [i for i in filtered_industries if i['status'] == status_filter]
    if search:
        filtered_industries = [i for i in filtered_industries if 
                             search.lower() in i['name'].lower() or 
                             search.lower() in i['contact_person'].lower() or
                             search in i['id']]
    if sector_filter:
        filtered_industries = [i for i in filtered_industries if i['sector'] == sector_filter]
    
    sectors = list(set(i['sector'] for i in admin_industries_data))
    
    # Industry statistics
    industry_stats = {
        'total': len(admin_industries_data),
        'verified': len([i for i in admin_industries_data if i['status'] == 'Verified']),
        'pending': len([i for i in admin_industries_data if i['status'] == 'Pending']),
        'total_credits_purchased': sum(i['credits_purchased'] for i in admin_industries_data),
        'total_revenue_generated': sum(i['revenue_contributed'] for i in admin_industries_data)
    }
    
    return render_template('admin/industries.html',
                         industries=filtered_industries,
                         stats=industry_stats,
                         status_filter=status_filter,
                         search=search,
                         sector_filter=sector_filter,
                         sectors=sectors)

@admin_bp.route("/industries/<industry_id>")
def industry_details(industry_id):
    """Detailed view of a specific industry"""
    generate_comprehensive_admin_data()
    
    industry = next((i for i in admin_industries_data if i['id'] == industry_id), None)
    if not industry:
        flash('Industry not found', 'error')
        return redirect(url_for('admin.industries_management'))
    
    return render_template('admin/industry_details.html', industry=industry)

@admin_bp.route("/industries/<industry_id>/action", methods=['POST'])
def industry_action(industry_id):
    """Handle industry actions (verify, blacklist, edit)"""
    generate_comprehensive_admin_data()
    
    action = request.form.get('action')
    reason = request.form.get('reason', '')
    
    industry = next((i for i in admin_industries_data if i['id'] == industry_id), None)
    if not industry:
        return jsonify({'success': False, 'message': 'Industry not found'})
    
    if action == 'verify':
        industry['status'] = 'Verified'
        industry['verification_date'] = datetime.now()
        message = f'Industry {industry["name"]} verified successfully'
        
    elif action == 'blacklist':
        industry['status'] = 'Blacklisted'
        industry['blacklist_reason'] = reason
        message = f'Industry {industry["name"]} blacklisted successfully'
        
    elif action == 'edit':
        # Handle edit form data
        industry['contact_person'] = request.form.get('contact_person', industry['contact_person'])
        industry['phone'] = request.form.get('phone', industry['phone'])
        industry['email'] = request.form.get('email', industry['email'])
        message = f'Industry {industry["name"]} information updated successfully'
    
    return jsonify({'success': True, 'message': message})

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

@app.route("/")
def landing_page():
    return render_template("index.html")

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

@industry_bp.route("/login")
def industry_login():
    """Industry Login Page"""
    return render_template('industry/login.html')

@industry_bp.route("/dashboard")
def dashboard():
    """Industry Dashboard"""
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
        credits = int(request.form.get('credits', 0))
        payment_method = request.form.get('payment_method', 'wallet')
        
        if credits <= 0 or credits > project['available_credits']:
            return jsonify({'success': False, 'message': 'Invalid credit amount'})
        
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
        
        # Update industry stats
        industry_user_data['credits_purchased'] += credits
        industry_user_data['credits_active'] += credits
        industry_user_data['total_spent'] += total_cost
        
        return jsonify({
            'success': True, 
            'message': f'Successfully purchased {credits} credits for ₹{total_cost:,}',
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

if __name__ == "__main__":
    app.register_blueprint(admin_bp)
    app.register_blueprint(ngo_bp)
    app.register_blueprint(industry_bp)
    app.run(debug=True)
