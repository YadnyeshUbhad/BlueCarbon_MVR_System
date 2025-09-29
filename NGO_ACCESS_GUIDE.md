# 🌱 NGO Portal Access Guide

## 🔐 **LOGIN CREDENTIALS**

### **NGO Test Account:**
- **📧 Email:** `ngo@example.org`
- **🔒 Password:** `Ngo@123`
- **👤 Role:** NGO
- **🏢 Organization:** Green Earth Foundation

## 🌐 **ACCESS URLs**

### **Direct Links (Copy-Paste into Browser):**
1. **🏠 NGO Portal Home:** `http://127.0.0.1:5000/ngo/`
2. **🔑 NGO Login:** `http://127.0.0.1:5000/ngo/login`
3. **📝 NGO Registration:** `http://127.0.0.1:5000/ngo/register`

## 🚀 **Step-by-Step Access:**

### **Method 1: Direct Browser Access**
1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Copy and paste this URL: `http://127.0.0.1:5000/ngo/login`
3. Press Enter
4. Login with:
   - **Email:** ngo@example.org
   - **Password:** Ngo@123
5. Click "Login"

### **Method 2: From Landing Page**
1. Go to: `http://127.0.0.1:5000/`
2. Click on "Access NGO Portal" button
3. Login with the credentials above

## 📋 **NGO Portal Features Available:**

Once logged in, you'll have access to:

### **✅ Dashboard:**
- Project statistics
- Credits earned
- Revenue information
- Recent activities

### **✅ Project Management:**
- Submit new projects with file uploads
- View existing projects
- Track project status
- Upload baseline conditions and plant images

### **✅ File Upload Features (NEW):**
- **Baseline Condition Upload:** PDF, DOC, images, Excel files
- **Plant Images:** Multiple image upload with gallery view
- **GPS Location:** Exact coordinates capture and satellite maps

### **✅ Credits & Revenue:**
- View earned credits
- Export credit data to CSV
- Revenue tracking and payout requests

### **✅ Profile Management:**
- Update NGO information
- Bank account details
- Two-factor authentication setup

## 🧪 **Testing New Features:**

### **Project Submission with Files:**
1. Go to **Projects** → **New Project**
2. Fill out project details
3. **Upload baseline condition file** (use `test_baseline_condition.txt`)
4. **Upload plant images** (use test images we created)
5. **Set location coordinates:** 19.0176, 72.8562 (Mumbai)
6. Calculate carbon credits and submit

### **Admin Portal Verification:**
1. Open new tab: `http://127.0.0.1:5000/admin/login`
2. Login as admin:
   - **Email:** admin@nccr.gov
   - **Password:** Admin@123
3. Go to **Projects** → Find your submitted project
4. Click **View Details** to see:
   - ✅ GPS coordinates with satellite map
   - ✅ Baseline condition file download
   - ✅ Plant images gallery
   - ✅ Real-time project data

## 🔧 **Troubleshooting:**

### **If NGO portal doesn't load:**
1. Check if server is running: `python app.py`
2. Verify URL: `http://127.0.0.1:5000/ngo/login`
3. Try clearing browser cache
4. Check firewall/antivirus settings

### **If login fails:**
1. Ensure exact credentials:
   - Email: `ngo@example.org` (with .org, not .com)
   - Password: `Ngo@123` (capital N, capital @)
2. Check if CAPS LOCK is on
3. Try typing manually instead of copy-paste

### **If features are missing:**
1. Ensure you're logged in as NGO role
2. Check browser console for JavaScript errors
3. Refresh the page

## 🎯 **Other Test Accounts:**

### **Admin Account:**
- **Email:** admin@nccr.gov
- **Password:** Admin@123

### **Industry Account:**
- **Email:** industry@example.com  
- **Password:** Industry@123

---

## 🌟 **What You Should See:**

### **After Login:**
- NGO Dashboard with statistics
- Navigation menu with Projects, Credits, Profile, etc.
- Your NGO name: "Green Earth Foundation"

### **In Project Submission:**
- File upload options for baseline conditions
- Multiple image upload for plant photos
- Interactive map for location selection
- Carbon credit calculator

### **In Admin Portal (after submitting project):**
- Your project appears immediately
- GPS coordinates shown on satellite map
- Uploaded files viewable and downloadable
- Complete project information display

---

**🎉 Enjoy testing the enhanced BlueCarbon MRV system!**

**Status: All features are 100% functional and ready to use!** ✅