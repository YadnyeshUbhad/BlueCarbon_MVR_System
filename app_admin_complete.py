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
                         status_filter=status_filter)

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
        project['status'] = 'Verified'
        project['approval_date'] = datetime.now()
        project['token_id'] = f'BC{random.randint(100000, 999999)}'
        project['credits_approved'] = project['credits_requested']
        message = f'Project {project_id} approved and credits issued successfully'
        
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

if __name__ == "__main__":
    app.register_blueprint(admin_bp)
    app.run(debug=True)