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
                'status': status,
                'submission_date': datetime.now() - timedelta(days=random.randint(1, 60)),
                'credits_requested': random.randint(50, 500),
                'verification_notes': 'Sample verification notes for this project' if status != 'Pending Review' else '',
                'last_updated': datetime.now() - timedelta(days=random.randint(0, 30))
            })
    
    if not admin_ngos_data:
        # Sample NGOs for admin review
        for i in range(10):
            status = random.choice(['Verified', 'Pending', 'Blacklisted'])
            admin_ngos_data.append({
                'id': f'NGO{2000 + i}',
                'name': random.choice(['Green Earth NGO', 'Coastal Conservation Trust', 'Marine Life Foundation', 'Blue Planet Initiative', 'Ocean Guardians']),
                'registration_number': f'NGO/REG/2020/{1000 + i}',
                'status': status,
                'projects_count': random.randint(1, 15),
                'registration_date': datetime.now() - timedelta(days=random.randint(30, 1000))
            })
    
    if not admin_industries_data:
        # Sample industries for admin review
        for i in range(15):
            status = random.choice(['Verified', 'Pending'])
            admin_industries_data.append({
                'id': f'IND{3000 + i}',
                'name': random.choice(['EcoTech Corp', 'Green Industries Ltd', 'Carbon Offset Solutions', 'CleanTech International', 'Sustainable Corp']),
                'industry_type': random.choice(['Manufacturing', 'Technology', 'Energy', 'Transportation']),
                'status': status,
                'credits_purchased': random.randint(50, 2000),
                'revenue_contributed': random.randint(10000, 500000),
                'registration_date': datetime.now() - timedelta(days=random.randint(30, 800))
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

# NCCR Admin blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
def admin_dashboard():
    """NCCR Admin Dashboard with overview of all projects, NGOs, and transactions"""
    generate_admin_dummy_data()
    
    # Calculate statistics
    total_projects = len(admin_projects_data)
    pending_verification = len([p for p in admin_projects_data if p['status'] in ['Pending Review', 'Documents Missing', 'Under Verification']])
    verified_projects = len([p for p in admin_projects_data if p['status'] == 'Verified'])
    total_credits_generated = sum(p['credits_requested'] for p in admin_projects_data)
    total_credits_verified = sum(p['credits_requested'] for p in admin_projects_data if p['status'] == 'Verified')
    
    # Generate dummy transactions if needed
    if not transactions_data:
        generate_dummy_transactions()
    
    total_revenue_distributed = sum(t['total'] for t in transactions_data if t.get('status') == 'Completed')
    
    # NGO statistics
    total_ngos = len(admin_ngos_data) if admin_ngos_data else 5
    verified_ngos = len([n for n in admin_ngos_data if n.get('status') == 'Verified']) if admin_ngos_data else 3
    pending_ngos = len([n for n in admin_ngos_data if n.get('status') == 'Pending']) if admin_ngos_data else 2
    blacklisted_ngos = len([n for n in admin_ngos_data if n.get('status') == 'Blacklisted']) if admin_ngos_data else 0
    
    # Industry statistics
    total_industries = len(admin_industries_data) if admin_industries_data else 8
    verified_industries = len([i for i in admin_industries_data if i.get('status') == 'Verified']) if admin_industries_data else 6
    pending_industries = len([i for i in admin_industries_data if i.get('status') == 'Pending']) if admin_industries_data else 2
    total_credits_purchased = sum(i.get('credits_purchased', 0) for i in admin_industries_data) if admin_industries_data else 1200
    total_revenue_generated = sum(i.get('revenue_contributed', 0) for i in admin_industries_data) if admin_industries_data else 240000
    
    # Recent activities for the template
    activities = [
        {
            'title': 'Mangrove Restoration Project verified and approved',
            'time': '2 hours ago',
            'type': 'success'
        },
        {
            'title': 'New NGO "Coastal Guardians" registered',
            'time': '5 hours ago',
            'type': 'info'
        },
        {
            'title': 'EcoTech Corp purchased 150 carbon credits',
            'time': '1 day ago',
            'type': 'success'
        },
        {
            'title': 'Seagrass project rejected due to insufficient documentation',
            'time': '2 days ago',
            'type': 'warning'
        }
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
def admin_projects():
    """Admin projects management page - returns JSON data"""
    generate_admin_dummy_data()
    
    # Filter projects based on query parameters
    status_filter = request.args.get('status', '')
    search_query = request.args.get('q', '')
    
    filtered_projects = admin_projects_data.copy()
    if status_filter:
        filtered_projects = [p for p in filtered_projects if p['status'] == status_filter]
    if search_query:
        filtered_projects = [p for p in filtered_projects if search_query.lower() in p['name'].lower() or search_query.lower() in p['ngo_name'].lower()]
    
    # Convert datetime objects to strings for JSON serialization
    for project in filtered_projects:
        if 'submission_date' in project and isinstance(project['submission_date'], datetime):
            project['submission_date'] = project['submission_date'].strftime('%Y-%m-%d')
        if 'last_updated' in project and isinstance(project['last_updated'], datetime):
            project['last_updated'] = project['last_updated'].strftime('%Y-%m-%d')
    
    return jsonify({
        'projects': filtered_projects,
        'total': len(filtered_projects),
        'status_filter': status_filter,
        'search_query': search_query
    })

@admin_bp.route("/ngos")
def admin_ngos():
    """Admin NGOs management page - returns JSON data"""
    generate_admin_dummy_data()
    
    status_filter = request.args.get('status', '')
    filtered_ngos = admin_ngos_data.copy()
    if status_filter:
        filtered_ngos = [n for n in filtered_ngos if n['status'] == status_filter]
    
    # Convert datetime objects to strings
    for ngo in filtered_ngos:
        if 'registration_date' in ngo and isinstance(ngo['registration_date'], datetime):
            ngo['registration_date'] = ngo['registration_date'].strftime('%Y-%m-%d')
    
    return jsonify({
        'ngos': filtered_ngos,
        'total': len(filtered_ngos),
        'status_filter': status_filter
    })

@admin_bp.route("/industries")
def admin_industries():
    """Admin industries management page - returns JSON data"""
    generate_admin_dummy_data()
    
    status_filter = request.args.get('status', '')
    filtered_industries = admin_industries_data.copy()
    if status_filter:
        filtered_industries = [i for i in filtered_industries if i['status'] == status_filter]
    
    # Convert datetime objects to strings
    for industry in filtered_industries:
        if 'registration_date' in industry and isinstance(industry['registration_date'], datetime):
            industry['registration_date'] = industry['registration_date'].strftime('%Y-%m-%d')
    
    return jsonify({
        'industries': filtered_industries,
        'total': len(filtered_industries),
        'status_filter': status_filter
    })

@admin_bp.route("/revenue")
def admin_revenue():
    """Admin revenue tracking page - returns JSON data"""
    if not transactions_data:
        generate_dummy_transactions()
    
    # Convert datetime objects to strings for JSON serialization
    transactions_for_json = []
    for t in transactions_data:
        t_copy = t.copy()
        if isinstance(t_copy['date'], datetime):
            t_copy['date'] = t_copy['date'].strftime('%Y-%m-%d')
        transactions_for_json.append(t_copy)
    
    revenue_summary = {
        'total_transactions': len(transactions_data),
        'total_revenue': sum(t['total'] for t in transactions_data if t['status'] == 'Completed'),
        'pending_revenue': sum(t['total'] for t in transactions_data if t['status'] == 'Pending')
    }
    
    return jsonify({
        'summary': revenue_summary,
        'transactions': transactions_for_json
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
        }
    ]
    
    return render_template("ngo/dashboard.html", stats=stats, recent_activities=recent_activities)

@app.route("/_routes")
def list_routes():
    lines = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        lines.append(f"{methods}\t{rule.endpoint}\t{rule}")
    return Response("\n".join(sorted(lines)), mimetype="text/plain")

if __name__ == "__main__":
    app.register_blueprint(ngo_bp)
    app.register_blueprint(admin_bp)
    app.run(debug=True)