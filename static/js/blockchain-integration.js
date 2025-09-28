/**
 * Blockchain Integration JavaScript for BlueCarbon MRV System
 * Provides frontend functions to interact with blockchain APIs
 */

// API base URL
const BLOCKCHAIN_API_BASE = '/api/blockchain';

// Utility function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        font-weight: 500;
        z-index: 10000;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Blockchain API wrapper class
class BlockchainAPI {
    static async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${BLOCKCHAIN_API_BASE}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('Blockchain API Error:', error);
            throw error;
        }
    }

    // Get blockchain statistics
    static async getStats() {
        return await this.request('/stats');
    }

    // Tokenize a project (create blockchain tokens)
    static async tokenizeProject(projectId, creditsAmount, metadata = {}) {
        return await this.request(`/projects/${projectId}/tokenize`, {
            method: 'POST',
            body: JSON.stringify({
                credits_amount: creditsAmount,
                metadata: metadata
            })
        });
    }

    // Transfer tokens between addresses
    static async transferToken(tokenId, fromAddress, toAddress, amount) {
        return await this.request(`/tokens/${tokenId}/transfer`, {
            method: 'POST',
            body: JSON.stringify({
                from_address: fromAddress,
                to_address: toAddress,
                amount: amount
            })
        });
    }

    // Retire tokens for carbon offsetting
    static async retireToken(tokenId, ownerAddress, reason = 'Carbon offsetting') {
        return await this.request(`/tokens/${tokenId}/retire`, {
            method: 'POST',
            body: JSON.stringify({
                owner_address: ownerAddress,
                reason: reason
            })
        });
    }

    // Get token information
    static async getTokenInfo(tokenId) {
        return await this.request(`/tokens/${tokenId}`);
    }

    // List tokens with filters
    static async listTokens(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/tokens?${params.toString()}`);
    }

    // List transactions with filters
    static async listTransactions(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/transactions?${params.toString()}`);
    }

    // Get token flow visualization
    static async getTokenFlowVisualization(projectId = null, timeframeDays = 365) {
        const params = new URLSearchParams();
        if (projectId) params.set('project_id', projectId);
        params.set('timeframe_days', timeframeDays);
        return await this.request(`/visualization/token-flow?${params.toString()}`);
    }

    // Get real-time dashboard data
    static async getRealTimeDashboard(projectId = null) {
        const params = new URLSearchParams();
        if (projectId) params.set('project_id', projectId);
        return await this.request(`/visualization/real-time-dashboard?${params.toString()}`);
    }

    // Verify transaction by hash
    static async verifyTransaction(txHash) {
        return await this.request(`/verify-transaction/${txHash}`);
    }

    // Get wallet balance
    static async getWalletBalance(address) {
        return await this.request(`/wallet/${address}/balance`);
    }

    // Get smart contract info
    static async getSmartContractInfo() {
        return await this.request('/smart-contract/info');
    }
}

// Enhanced functions for specific UI interactions
class BlockchainUI {
    // Initialize blockchain widgets on page load
    static init() {
        this.loadBlockchainStats();
        this.setupRealTimeUpdates();
    }

    // Load and display blockchain statistics
    static async loadBlockchainStats() {
        try {
            const response = await BlockchainAPI.getStats();
            const stats = response.data;
            
            // Update stats in any blockchain stat containers
            this.updateStatsDisplay(stats);
        } catch (error) {
            console.error('Failed to load blockchain stats:', error);
        }
    }

    // Update stats display elements
    static updateStatsDisplay(stats) {
        // Update total supply
        const totalSupplyEl = document.getElementById('blockchain-total-supply');
        if (totalSupplyEl) {
            totalSupplyEl.textContent = stats.total_tokens_issued || 0;
        }

        // Update active supply
        const activeSupplyEl = document.getElementById('blockchain-active-supply');
        if (activeSupplyEl) {
            activeSupplyEl.textContent = (stats.total_tokens_issued - stats.total_tokens_retired) || 0;
        }

        // Update transaction count
        const txCountEl = document.getElementById('blockchain-tx-count');
        if (txCountEl) {
            txCountEl.textContent = stats.total_transactions || 0;
        }

        // Update verification status
        const verifiedEl = document.getElementById('blockchain-verified');
        if (verifiedEl) {
            verifiedEl.innerHTML = '<i class="fas fa-check-circle"></i> Verified';
            verifiedEl.className = 'blockchain-status verified';
        }
    }

    // Setup real-time updates (polling)
    static setupRealTimeUpdates() {
        // Update blockchain stats every 30 seconds
        setInterval(() => {
            this.loadBlockchainStats();
        }, 30000);

        // Update real-time dashboard if element exists
        const dashboardEl = document.getElementById('blockchain-dashboard');
        if (dashboardEl) {
            this.updateRealTimeDashboard();
            setInterval(() => {
                this.updateRealTimeDashboard();
            }, 10000);
        }
    }

    // Update real-time dashboard
    static async updateRealTimeDashboard() {
        try {
            const response = await BlockchainAPI.getRealTimeDashboard();
            const data = response.data;
            
            const dashboardEl = document.getElementById('blockchain-dashboard');
            if (dashboardEl) {
                dashboardEl.innerHTML = this.renderDashboardHTML(data);
            }
        } catch (error) {
            console.error('Failed to update real-time dashboard:', error);
        }
    }

    // Render dashboard HTML
    static renderDashboardHTML(data) {
        return `
            <div class="blockchain-dashboard-grid">
                <div class="dashboard-card">
                    <h4>Total Tokens</h4>
                    <div class="dashboard-value">${data.network_stats?.total_tokens || 0}</div>
                </div>
                <div class="dashboard-card">
                    <h4>Active Projects</h4>
                    <div class="dashboard-value">${data.network_stats?.active_projects || 0}</div>
                </div>
                <div class="dashboard-card">
                    <h4>Recent Transactions</h4>
                    <div class="dashboard-value">${data.network_stats?.recent_transactions || 0}</div>
                </div>
                <div class="dashboard-card">
                    <h4>Network Health</h4>
                    <div class="dashboard-value health-good">
                        <i class="fas fa-heart"></i> Healthy
                    </div>
                </div>
            </div>
        `;
    }

    // Handle project tokenization
    static async handleTokenizeProject(projectId, creditsAmount, projectData = {}) {
        try {
            showNotification('Creating blockchain tokens...', 'info');
            
            const response = await BlockchainAPI.tokenizeProject(projectId, creditsAmount, {
                project_name: projectData.name,
                ecosystem: projectData.ecosystem,
                location: projectData.location,
                ngo_name: projectData.ngo_name
            });
            
            if (response.success) {
                showNotification(`Successfully created ${creditsAmount} carbon credit tokens!`, 'success');
                
                // Update UI with token information
                this.displayTokenInfo(response.data);
                
                // Refresh blockchain stats
                this.loadBlockchainStats();
                
                return response.data;
            }
        } catch (error) {
            showNotification(`Failed to create tokens: ${error.message}`, 'error');
            throw error;
        }
    }

    // Display token information in UI
    static displayTokenInfo(tokenData) {
        const tokenInfoEl = document.getElementById('token-info-display');
        if (tokenInfoEl) {
            tokenInfoEl.innerHTML = `
                <div class="token-info-card">
                    <h4>🪙 Token Created Successfully</h4>
                    <div class="token-details">
                        <div><strong>Token ID:</strong> <code>${tokenData.token_id}</code></div>
                        <div><strong>Credits Amount:</strong> ${tokenData.credits_amount} tCO₂e</div>
                        <div><strong>Blockchain Hash:</strong> <code>${tokenData.blockchain_hash}</code></div>
                        <div><strong>Created:</strong> ${new Date(tokenData.created_at).toLocaleString()}</div>
                    </div>
                    <div class="token-actions">
                        <button onclick="BlockchainUI.viewOnBlockchain('${tokenData.blockchain_hash}')" class="btn btn-outline">
                            <i class="fas fa-external-link-alt"></i> View on Blockchain
                        </button>
                    </div>
                </div>
            `;
        }
    }

    // Handle token retirement
    static async handleRetireToken(tokenId, ownerAddress, amount, reason = 'Carbon offsetting') {
        try {
            showNotification('Retiring carbon credits...', 'info');
            
            const response = await BlockchainAPI.retireToken(tokenId, ownerAddress, reason);
            
            if (response.success) {
                showNotification(`Successfully retired ${amount} carbon credits!`, 'success');
                
                // Update UI to show retired status
                this.markTokenAsRetired(tokenId);
                
                // Refresh stats
                this.loadBlockchainStats();
                
                return response.data;
            }
        } catch (error) {
            showNotification(`Failed to retire tokens: ${error.message}`, 'error');
            throw error;
        }
    }

    // Mark token as retired in UI
    static markTokenAsRetired(tokenId) {
        const tokenElements = document.querySelectorAll(`[data-token-id="${tokenId}"]`);
        tokenElements.forEach(el => {
            el.classList.add('token-retired');
            el.querySelector('.token-status')?.innerHTML = '<i class="fas fa-check-circle"></i> Retired';
        });
    }

    // View transaction on blockchain explorer (mock)
    static viewOnBlockchain(hash) {
        // In a real implementation, this would open the blockchain explorer
        showNotification(`Viewing transaction ${hash} on blockchain explorer`, 'info');
        window.open(`https://explorer.bluecarbon.testnet/tx/${hash}`, '_blank');
    }

    // Load and display recent transactions
    static async loadRecentTransactions(limit = 10) {
        try {
            const response = await BlockchainAPI.listTransactions({ limit });
            const transactions = response.data.transactions;
            
            const transactionsEl = document.getElementById('recent-transactions');
            if (transactionsEl) {
                transactionsEl.innerHTML = this.renderTransactionsHTML(transactions);
            }
        } catch (error) {
            console.error('Failed to load recent transactions:', error);
        }
    }

    // Render transactions HTML
    static renderTransactionsHTML(transactions) {
        if (!transactions.length) {
            return '<div class="no-transactions">No recent transactions</div>';
        }

        return transactions.map(tx => `
            <div class="transaction-item">
                <div class="transaction-header">
                    <span class="transaction-type">${tx.type}</span>
                    <span class="transaction-time">${new Date(tx.datetime).toLocaleString()}</span>
                </div>
                <div class="transaction-details">
                    <div>Hash: <code>${tx.tx_hash}</code></div>
                    ${tx.data.token_id ? `<div>Token: ${tx.data.token_id}</div>` : ''}
                    ${tx.data.credits_amount ? `<div>Amount: ${tx.data.credits_amount} tCO₂e</div>` : ''}
                </div>
            </div>
        `).join('');
    }
}

// Global functions for template usage
window.BlockchainAPI = BlockchainAPI;
window.BlockchainUI = BlockchainUI;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    BlockchainUI.init();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BlockchainAPI, BlockchainUI };
}