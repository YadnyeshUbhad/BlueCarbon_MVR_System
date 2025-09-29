#!/usr/bin/env python3
"""
Test file to create sample upload files for testing baseline and media upload functionality
"""

import os
from PIL import Image
import json

def create_test_files():
    """Create sample files for testing upload functionality"""
    
    # Create test baseline files
    baseline_content = """
    BASELINE CONDITION REPORT
    =========================
    
    Project: Test Mangrove Restoration Project
    Location: Mumbai Coastal Area
    Date: 2025-09-29
    
    Initial Ecosystem Assessment:
    - Existing vegetation coverage: 15%
    - Soil salinity levels: High (suitable for mangroves)
    - Water quality: Moderate
    - Biodiversity index: 2.3/10
    
    Baseline Measurements:
    - Total area surveyed: 5.2 hectares
    - Number of existing mature trees: 23
    - Average canopy height: 3.2 meters
    - Seedling survival rate (historical): 65%
    
    Environmental Conditions:
    - Average tide levels: 1.2m - 2.8m
    - Soil pH: 7.2 - 7.8
    - Temperature range: 24°C - 32°C
    - Annual rainfall: 1,200mm
    
    Pre-project Carbon Stock Estimation:
    - Above ground biomass: 12.5 tCO2e
    - Below ground biomass: 8.3 tCO2e
    - Total baseline carbon: 20.8 tCO2e
    
    Recommendations:
    - Plant native mangrove species (Rhizophora, Avicennia)
    - Regular monitoring required
    - Community engagement essential
    
    Report prepared by: Marine Ecosystem Research Team
    Verification: Pending field validation
    """
    
    with open('test_baseline_condition.txt', 'w', encoding='utf-8') as f:
        f.write(baseline_content)
    
    # Create sample plant images (simple colored rectangles for testing)
    test_images = [
        ('test_mangrove_1.png', (0, 128, 0)),  # Green for mangrove
        ('test_mangrove_2.png', (34, 139, 34)),  # Forest green
        ('test_coastal_vegetation.png', (50, 205, 50)),  # Lime green
        ('test_seedling_nursery.png', (124, 252, 0))  # Lawn green
    ]
    
    for filename, color in test_images:
        img = Image.new('RGB', (400, 300), color)
        # Add some simple "vegetation" pattern
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw some tree-like shapes
        for i in range(10):
            x = 40 + i * 35
            y = 250
            # Tree trunk
            draw.rectangle([x-2, y-30, x+2, y], fill=(101, 67, 33))
            # Tree canopy
            draw.ellipse([x-15, y-60, x+15, y-30], fill=(0, 100, 0))
        
        # Add text overlay
        from PIL import ImageFont
        try:
            font = ImageFont.load_default()
            draw.text((10, 10), f"Plant Image - {filename[:-4].replace('_', ' ').title()}", 
                     fill=(255, 255, 255), font=font)
            draw.text((10, 280), "Sample for BlueCarbon MRV Testing", 
                     fill=(255, 255, 255), font=font)
        except:
            pass  # Ignore font errors
        
        img.save(filename)
        print(f"Created test image: {filename}")
    
    # Create test location data
    test_location = {
        "lat": 19.0176,  # Mumbai coordinates
        "lng": 72.8562,
        "address": "Mumbai Coastal Area, Maharashtra, India",
        "area": 5.2,
        "ecosystem": "Mangrove"
    }
    
    with open('test_location_data.json', 'w') as f:
        json.dump(test_location, f, indent=2)
    
    print("\n✅ Test files created successfully!")
    print("Files created:")
    print("- test_baseline_condition.txt (Baseline condition document)")
    print("- test_mangrove_1.png (Sample plant image 1)")
    print("- test_mangrove_2.png (Sample plant image 2)")  
    print("- test_coastal_vegetation.png (Sample plant image 3)")
    print("- test_seedling_nursery.png (Sample plant image 4)")
    print("- test_location_data.json (GPS coordinates)")
    print("\n🧪 You can now use these files to test the upload functionality!")
    print("📍 Test coordinates: 19.0176, 72.8562 (Mumbai)")

if __name__ == "__main__":
    create_test_files()