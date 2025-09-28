#!/usr/bin/env python3
"""
Full Stack Deployment Script for Blue Carbon MRV System
Starts blockchain node and Flask application
"""

import subprocess
import time
import os
import sys
import signal
import threading
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*80)
    print("🌊 BLUE CARBON MRV FULL STACK DEPLOYMENT")
    print("="*80)
    print("Starting blockchain-enabled carbon credit management system...")
    print("="*80 + "\n")

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if blockchain contracts are deployed
    contracts_file = Path("blockchain/.env.contracts")
    if not contracts_file.exists():
        print("❌ Smart contracts not deployed!")
        print("   Run: cd blockchain && npm run deploy:localhost")
        return False
    
    # Check if Node.js is available
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Node.js not found")
        print(f"✅ Node.js: {result.stdout.strip()}")
    except Exception:
        print("❌ Node.js not found! Please install Node.js")
        return False
    
    # Check if Python dependencies are available
    try:
        import flask, web3
        print("✅ Python dependencies: OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("   Run: pip install flask web3")
        return False
    
    print("✅ All requirements met!\n")
    return True

def start_blockchain_node():
    """Start local blockchain node (Hardhat)"""
    print("🔗 Starting local blockchain node...")
    
    try:
        # Start Hardhat node in blockchain directory
        os.chdir("blockchain")
        
        # Check if contracts are compiled
        if not Path("artifacts").exists():
            print("📦 Compiling smart contracts...")
            compile_result = subprocess.run(['npm', 'run', 'compile'], capture_output=True, text=True)
            if compile_result.returncode != 0:
                print(f"❌ Compilation failed: {compile_result.stderr}")
                return None
            print("✅ Smart contracts compiled")
        
        # Start Hardhat node
        print("🚀 Starting Hardhat blockchain node...")
        blockchain_process = subprocess.Popen(
            ['npx', 'hardhat', 'node'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for node to start
        time.sleep(5)
        
        if blockchain_process.poll() is None:
            print("✅ Blockchain node started (localhost:8545)")
            
            # Deploy contracts if needed
            print("📋 Deploying smart contracts...")
            deploy_result = subprocess.run(
                ['npx', 'hardhat', 'run', 'scripts/deploy.js', '--network', 'localhost'],
                capture_output=True,
                text=True
            )
            
            if deploy_result.returncode == 0:
                print("✅ Smart contracts deployed successfully")
            else:
                print(f"⚠️  Contract deployment issue: {deploy_result.stderr}")
            
            return blockchain_process
        else:
            print("❌ Failed to start blockchain node")
            return None
            
    except Exception as e:
        print(f"❌ Error starting blockchain: {e}")
        return None
    finally:
        os.chdir("..")

def start_flask_app():
    """Start Flask application"""
    print("🌐 Starting Flask application...")
    
    try:
        # Start Flask app
        flask_process = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for Flask to start
        time.sleep(3)
        
        if flask_process.poll() is None:
            print("✅ Flask application started")
            print("🌐 Web interface: http://127.0.0.1:5000")
            print("📊 Admin dashboard: http://127.0.0.1:5000/admin/login")
            print("🔗 Blockchain API: http://127.0.0.1:5000/api/real_blockchain/status")
            return flask_process
        else:
            print("❌ Failed to start Flask application")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return None

def monitor_processes(blockchain_process, flask_process):
    """Monitor both processes and restart if needed"""
    print("\n📊 Monitoring processes...")
    print("Press Ctrl+C to stop all services\n")
    
    try:
        while True:
            time.sleep(5)
            
            # Check blockchain process
            if blockchain_process and blockchain_process.poll() is not None:
                print("⚠️  Blockchain node stopped unexpectedly")
                break
            
            # Check Flask process
            if flask_process and flask_process.poll() is not None:
                print("⚠️  Flask application stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        
        # Terminate processes gracefully
        if blockchain_process:
            print("⏸️  Stopping blockchain node...")
            blockchain_process.terminate()
            try:
                blockchain_process.wait(timeout=10)
                print("✅ Blockchain node stopped")
            except subprocess.TimeoutExpired:
                blockchain_process.kill()
                print("🔥 Blockchain node force killed")
        
        if flask_process:
            print("⏸️  Stopping Flask application...")
            flask_process.terminate()
            try:
                flask_process.wait(timeout=10)
                print("✅ Flask application stopped")
            except subprocess.TimeoutExpired:
                flask_process.kill()
                print("🔥 Flask application force killed")
        
        print("\n✅ All services stopped successfully")

def print_usage_info():
    """Print usage information"""
    print("\n" + "="*80)
    print("🎯 SYSTEM READY!")
    print("="*80)
    print("Your Blue Carbon MRV system is now running with:")
    print("  • Real blockchain network (Hardhat local)")
    print("  • Smart contracts deployed and functional")
    print("  • Complete web interface with admin dashboard")
    print("  • API endpoints for carbon credit management")
    print("\n🔗 Quick Links:")
    print("  • Main Dashboard: http://127.0.0.1:5000")
    print("  • Admin Login: http://127.0.0.1:5000/admin/login")
    print("  • NGO Dashboard: http://127.0.0.1:5000/ngo/dashboard") 
    print("  • Industry Portal: http://127.0.0.1:5000/industry/login")
    print("  • Blockchain Status: http://127.0.0.1:5000/api/real_blockchain/status")
    print("\n🧪 Test Carbon Credit Workflow:")
    print("  POST http://127.0.0.1:5000/api/real_blockchain/demo")
    print("  (Creates MRV record → Verifies → Mints credits)")
    print("\n⚠️  Note: This uses a local blockchain for development/testing")
    print("="*80 + "\n")

def main():
    """Main deployment function"""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    # Start blockchain node
    blockchain_process = start_blockchain_node()
    if not blockchain_process:
        print("❌ Failed to start blockchain node")
        sys.exit(1)
    
    # Wait a bit for blockchain to stabilize
    time.sleep(3)
    
    # Start Flask application
    flask_process = start_flask_app()
    if not flask_process:
        print("❌ Failed to start Flask application")
        if blockchain_process:
            blockchain_process.terminate()
        sys.exit(1)
    
    # Print usage information
    print_usage_info()
    
    # Monitor both processes
    monitor_processes(blockchain_process, flask_process)

if __name__ == "__main__":
    main()