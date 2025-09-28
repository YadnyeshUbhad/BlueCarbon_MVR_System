"""
Blockchain Token Visualization Module for BlueCarbon MRV System
Creates interactive dashboards showing tokenized credits flow, ownership transfers, and retirement tracking
"""

import numpy as np
import json
from datetime import datetime, timedelta
import random
import uuid

class TokenVisualizationEngine:
    def __init__(self):
        self.token_registry = {}
        self.transaction_history = []
        self.ownership_ledger = {}
        self.retirement_records = []
        
    def generate_token_flow_visualization(self, project_id=None, timeframe_days=365):
        """Generate comprehensive token flow visualization data"""
        
        # Filter data by project if specified
        if project_id:
            relevant_tokens = [t for t in self.token_registry.values() if t.get('project_id') == project_id]
            relevant_transactions = [t for t in self.transaction_history if t.get('project_id') == project_id]
        else:
            relevant_tokens = list(self.token_registry.values())
            relevant_transactions = self.transaction_history
        
        # Generate token flow data
        flow_data = self._create_token_flow_graph(relevant_tokens, relevant_transactions)
        ownership_distribution = self._analyze_ownership_distribution(relevant_tokens)
        temporal_analysis = self._analyze_temporal_patterns(relevant_transactions, timeframe_days)
        retirement_tracking = self._track_retirement_patterns(relevant_tokens)
        
        return {
            'visualization_id': f'TOKEN_VIZ_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'generation_timestamp': datetime.now().isoformat(),
            'project_filter': project_id,
            'timeframe_days': timeframe_days,
            'token_flow_graph': flow_data,
            'ownership_distribution': ownership_distribution,
            'temporal_analysis': temporal_analysis,
            'retirement_tracking': retirement_tracking,
            'summary_statistics': self._calculate_summary_stats(relevant_tokens, relevant_transactions)
        }
    
    def _create_token_flow_graph(self, tokens, transactions):
        """Create token flow graph showing movement between entities"""
        
        # Generate nodes (entities in the system)
        nodes = []
        edges = []
        node_registry = {}
        
        # Add system nodes
        system_nodes = [
            {'id': 'minting_authority', 'label': 'NCCR Minting Authority', 'type': 'authority', 'color': '#2563EB'},
            {'id': 'marketplace', 'label': 'Carbon Credit Marketplace', 'type': 'marketplace', 'color': '#059669'},
            {'id': 'retirement_pool', 'label': 'Retirement Pool', 'type': 'retirement', 'color': '#DC2626'}
        ]
        
        for node in system_nodes:
            nodes.append(node)
            node_registry[node['id']] = len(nodes) - 1
        
        # Add NGO nodes (token creators)
        ngo_entities = set()
        industry_entities = set()
        
        for token in tokens:
            ngo_id = token.get('creator_ngo', 'unknown_ngo')
            if ngo_id not in ngo_entities:
                ngo_entities.add(ngo_id)
                nodes.append({
                    'id': ngo_id,
                    'label': f'NGO {ngo_id[-4:]}',
                    'type': 'ngo',
                    'color': '#16A34A',
                    'tokens_created': len([t for t in tokens if t.get('creator_ngo') == ngo_id]),
                    'total_credits': sum(t.get('credit_amount', 0) for t in tokens if t.get('creator_ngo') == ngo_id)
                })
                node_registry[ngo_id] = len(nodes) - 1
        
        # Add Industry nodes (token buyers)
        for transaction in transactions:
            buyer_id = transaction.get('buyer_id', 'unknown_buyer')
            if buyer_id not in industry_entities and buyer_id.startswith('IND'):
                industry_entities.add(buyer_id)
                buyer_transactions = [t for t in transactions if t.get('buyer_id') == buyer_id]
                nodes.append({
                    'id': buyer_id,
                    'label': f'Industry {buyer_id[-4:]}',
                    'type': 'industry',
                    'color': '#EA580C',
                    'tokens_purchased': len(buyer_transactions),
                    'total_spent': sum(t.get('total_value', 0) for t in buyer_transactions)
                })
                node_registry[buyer_id] = len(nodes) - 1
        
        # Create edges (token flows)
        edge_weights = {}
        
        # Minting flows (Authority -> NGOs)
        for token in tokens:
            source = 'minting_authority'
            target = token.get('creator_ngo', 'unknown_ngo')
            edge_key = f"{source}->{target}"
            
            if edge_key not in edge_weights:
                edge_weights[edge_key] = {'count': 0, 'total_credits': 0, 'transactions': []}
            
            edge_weights[edge_key]['count'] += 1
            edge_weights[edge_key]['total_credits'] += token.get('credit_amount', 0)
            edge_weights[edge_key]['transactions'].append(token.get('token_id'))
        
        # Trading flows (NGOs -> Marketplace -> Industries)
        for transaction in transactions:
            if transaction.get('status') == 'Completed':
                # NGO to Marketplace
                ngo_id = transaction.get('seller_id', 'unknown_ngo')
                marketplace_key = f"{ngo_id}->marketplace"
                
                if marketplace_key not in edge_weights:
                    edge_weights[marketplace_key] = {'count': 0, 'total_credits': 0, 'transactions': []}
                
                edge_weights[marketplace_key]['count'] += 1
                edge_weights[marketplace_key]['total_credits'] += transaction.get('credits_sold', 0)
                edge_weights[marketplace_key]['transactions'].append(transaction.get('id'))
                
                # Marketplace to Industry
                industry_key = f"marketplace->{transaction.get('buyer_id', 'unknown_buyer')}"
                
                if industry_key not in edge_weights:
                    edge_weights[industry_key] = {'count': 0, 'total_credits': 0, 'transactions': []}
                
                edge_weights[industry_key]['count'] += 1
                edge_weights[industry_key]['total_credits'] += transaction.get('credits_sold', 0)
                edge_weights[industry_key]['transactions'].append(transaction.get('id'))
        
        # Convert edge weights to graph edges
        for edge_key, data in edge_weights.items():
            source, target = edge_key.split('->')
            if source in node_registry and target in node_registry:
                edges.append({
                    'id': edge_key,
                    'source': source,
                    'target': target,
                    'weight': data['total_credits'],
                    'transaction_count': data['count'],
                    'transactions': data['transactions'],
                    'label': f"{data['total_credits']:.1f} tCO₂e"
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'graph_density': len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
        }
    
    def _analyze_ownership_distribution(self, tokens):
        """Analyze current ownership distribution of tokens"""
        
        ownership_stats = {}
        
        for token in tokens:
            current_owner = token.get('current_owner', 'unknown')
            owner_type = self._classify_owner_type(current_owner)
            
            if owner_type not in ownership_stats:
                ownership_stats[owner_type] = {
                    'token_count': 0,
                    'total_credits': 0,
                    'entities': set(),
                    'avg_token_size': 0
                }
            
            ownership_stats[owner_type]['token_count'] += 1
            ownership_stats[owner_type]['total_credits'] += token.get('credit_amount', 0)
            ownership_stats[owner_type]['entities'].add(current_owner)
        
        # Calculate averages and percentages
        total_credits = sum(stats['total_credits'] for stats in ownership_stats.values())
        total_tokens = sum(stats['token_count'] for stats in ownership_stats.values())
        
        distribution_chart = []
        for owner_type, stats in ownership_stats.items():
            stats['avg_token_size'] = stats['total_credits'] / max(stats['token_count'], 1)
            stats['credit_percentage'] = (stats['total_credits'] / max(total_credits, 1)) * 100
            stats['token_percentage'] = (stats['token_count'] / max(total_tokens, 1)) * 100
            stats['entity_count'] = len(stats['entities'])
            
            # Convert set to list for JSON serialization
            stats['entities'] = list(stats['entities'])
            
            distribution_chart.append({
                'owner_type': owner_type,
                'percentage': stats['credit_percentage'],
                'credits': stats['total_credits'],
                'color': self._get_owner_type_color(owner_type)
            })
        
        return {
            'ownership_stats': ownership_stats,
            'distribution_chart': distribution_chart,
            'concentration_index': self._calculate_concentration_index(ownership_stats),
            'total_credits_in_circulation': total_credits,
            'total_active_tokens': total_tokens
        }
    
    def _classify_owner_type(self, owner_id):
        """Classify owner by entity type"""
        if not owner_id or owner_id == 'unknown':
            return 'unknown'
        elif owner_id.startswith('NGO'):
            return 'ngo'
        elif owner_id.startswith('IND'):
            return 'industry'
        elif 'marketplace' in owner_id.lower():
            return 'marketplace'
        elif 'authority' in owner_id.lower():
            return 'authority'
        else:
            return 'other'
    
    def _get_owner_type_color(self, owner_type):
        """Get color for owner type visualization"""
        colors = {
            'ngo': '#16A34A',
            'industry': '#EA580C',
            'marketplace': '#059669',
            'authority': '#2563EB',
            'unknown': '#6B7280',
            'other': '#8B5CF6'
        }
        return colors.get(owner_type, '#6B7280')
    
    def _analyze_temporal_patterns(self, transactions, timeframe_days):
        """Analyze temporal patterns in token transactions"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=timeframe_days)
        
        # Filter transactions by timeframe
        relevant_transactions = [
            t for t in transactions 
            if start_date <= datetime.fromisoformat(t.get('timestamp', datetime.now().isoformat())) <= end_date
        ]
        
        # Create time series data
        time_series = {}
        daily_volumes = {}
        monthly_volumes = {}
        
        for transaction in relevant_transactions:
            trans_date = datetime.fromisoformat(transaction.get('timestamp', datetime.now().isoformat()))
            date_key = trans_date.strftime('%Y-%m-%d')
            month_key = trans_date.strftime('%Y-%m')
            
            credits = transaction.get('credits_sold', 0)
            value = transaction.get('total_value', 0)
            
            # Daily aggregation
            if date_key not in daily_volumes:
                daily_volumes[date_key] = {'credits': 0, 'value': 0, 'count': 0}
            daily_volumes[date_key]['credits'] += credits
            daily_volumes[date_key]['value'] += value
            daily_volumes[date_key]['count'] += 1
            
            # Monthly aggregation
            if month_key not in monthly_volumes:
                monthly_volumes[month_key] = {'credits': 0, 'value': 0, 'count': 0}
            monthly_volumes[month_key]['credits'] += credits
            monthly_volumes[month_key]['value'] += value
            monthly_volumes[month_key]['count'] += 1
        
        # Generate trend analysis
        daily_data = sorted(daily_volumes.items())
        if len(daily_data) > 1:
            recent_volume = sum(d[1]['credits'] for d in daily_data[-7:])  # Last 7 days
            previous_volume = sum(d[1]['credits'] for d in daily_data[-14:-7])  # Previous 7 days
            volume_trend = ((recent_volume - previous_volume) / max(previous_volume, 1)) * 100
        else:
            volume_trend = 0
        
        return {
            'daily_volumes': dict(daily_volumes),
            'monthly_volumes': dict(monthly_volumes),
            'total_transactions': len(relevant_transactions),
            'total_credits_traded': sum(t.get('credits_sold', 0) for t in relevant_transactions),
            'total_value_traded': sum(t.get('total_value', 0) for t in relevant_transactions),
            'avg_transaction_size': np.mean([t.get('credits_sold', 0) for t in relevant_transactions]) if relevant_transactions else 0,
            'volume_trend_7d': volume_trend,
            'peak_trading_day': max(daily_volumes.items(), key=lambda x: x[1]['credits'])[0] if daily_volumes else None,
            'market_activity_score': min(len(relevant_transactions) / max(timeframe_days / 30, 1), 10)  # Transactions per month, capped at 10
        }
    
    def _track_retirement_patterns(self, tokens):
        """Track retirement patterns and environmental impact"""
        
        retired_tokens = [t for t in tokens if t.get('status') == 'retired']
        active_tokens = [t for t in tokens if t.get('status') == 'active']
        
        # Retirement analysis by ecosystem type
        retirement_by_ecosystem = {}
        retirement_by_vintage = {}
        retirement_by_industry = {}
        
        for token in retired_tokens:
            # By ecosystem
            ecosystem = token.get('ecosystem_type', 'unknown')
            if ecosystem not in retirement_by_ecosystem:
                retirement_by_ecosystem[ecosystem] = {'count': 0, 'credits': 0}
            retirement_by_ecosystem[ecosystem]['count'] += 1
            retirement_by_ecosystem[ecosystem]['credits'] += token.get('credit_amount', 0)
            
            # By vintage year
            vintage = token.get('vintage_year', 'unknown')
            if vintage not in retirement_by_vintage:
                retirement_by_vintage[vintage] = {'count': 0, 'credits': 0}
            retirement_by_vintage[vintage]['count'] += 1
            retirement_by_vintage[vintage]['credits'] += token.get('credit_amount', 0)
            
            # By retiring industry
            retiring_entity = token.get('retired_by', 'unknown')
            if retiring_entity not in retirement_by_industry:
                retirement_by_industry[retiring_entity] = {'count': 0, 'credits': 0}
            retirement_by_industry[retiring_entity]['count'] += 1
            retirement_by_industry[retiring_entity]['credits'] += token.get('credit_amount', 0)
        
        # Calculate retirement metrics
        total_credits_minted = sum(t.get('credit_amount', 0) for t in tokens)
        total_credits_retired = sum(t.get('credit_amount', 0) for t in retired_tokens)
        retirement_rate = (total_credits_retired / max(total_credits_minted, 1)) * 100
        
        # Environmental impact calculation
        co2_offset_tonnes = total_credits_retired
        equivalent_impacts = {
            'cars_off_road_1_year': co2_offset_tonnes / 4.6,  # Average car emits 4.6 tonnes CO2/year
            'flights_offset_hours': co2_offset_tonnes / 0.25,  # ~0.25 tonnes CO2 per flight hour
            'trees_planted_equivalent': co2_offset_tonnes / 0.02,  # Tree absorbs ~20kg CO2/year
            'households_carbon_neutral_days': (co2_offset_tonnes / 16) * 365  # Household emits ~16 tonnes/year
        }
        
        return {
            'total_tokens_retired': len(retired_tokens),
            'total_credits_retired': total_credits_retired,
            'retirement_rate_percentage': retirement_rate,
            'retirement_by_ecosystem': retirement_by_ecosystem,
            'retirement_by_vintage': retirement_by_vintage,
            'retirement_by_industry': retirement_by_industry,
            'environmental_impact': {
                'co2_offset_tonnes': co2_offset_tonnes,
                'equivalent_impacts': equivalent_impacts
            },
            'active_tokens_count': len(active_tokens),
            'active_credits_value': sum(t.get('credit_amount', 0) for t in active_tokens)
        }
    
    def _calculate_concentration_index(self, ownership_stats):
        """Calculate ownership concentration index (Herfindahl-Hirschman Index)"""
        total_credits = sum(stats['total_credits'] for stats in ownership_stats.values())
        if total_credits == 0:
            return 0
        
        hhi = sum((stats['total_credits'] / total_credits) ** 2 for stats in ownership_stats.values())
        return hhi * 10000  # Normalized to 0-10000 scale
    
    def _calculate_summary_stats(self, tokens, transactions):
        """Calculate summary statistics for the visualization"""
        
        total_tokens = len(tokens)
        total_credits = sum(t.get('credit_amount', 0) for t in tokens)
        total_transactions = len([t for t in transactions if t.get('status') == 'Completed'])
        total_volume_traded = sum(t.get('total_value', 0) for t in transactions if t.get('status') == 'Completed')
        
        # Calculate averages
        avg_token_size = total_credits / max(total_tokens, 1)
        avg_transaction_value = total_volume_traded / max(total_transactions, 1)
        
        # Market velocity (how often tokens change hands)
        unique_tokens_traded = len(set(t.get('token_id') for t in transactions if t.get('token_id')))
        market_velocity = unique_tokens_traded / max(total_tokens, 1)
        
        return {
            'total_tokens_minted': total_tokens,
            'total_credits_issued': total_credits,
            'total_completed_transactions': total_transactions,
            'total_market_value': total_volume_traded,
            'average_token_size': avg_token_size,
            'average_transaction_value': avg_transaction_value,
            'market_velocity': market_velocity,
            'market_maturity_score': min((total_transactions / max(total_tokens, 1)) * 5, 10)  # Scale 0-10
        }
    
    def create_real_time_dashboard_data(self, project_id=None):
        """Create real-time dashboard data for live token tracking"""
        
        # Simulate real-time token data
        current_time = datetime.now()
        
        # Generate sample token data if not already present
        if not self.token_registry:
            self._generate_sample_token_data()
        
        # Get recent activity (last 24 hours)
        recent_transactions = [
            t for t in self.transaction_history 
            if datetime.fromisoformat(t.get('timestamp', current_time.isoformat())) > current_time - timedelta(hours=24)
        ]
        
        # Live metrics
        live_metrics = {
            'active_tokens': len([t for t in self.token_registry.values() if t.get('status') == 'active']),
            'credits_in_circulation': sum(t.get('credit_amount', 0) for t in self.token_registry.values() if t.get('status') == 'active'),
            'transactions_24h': len(recent_transactions),
            'volume_24h': sum(t.get('total_value', 0) for t in recent_transactions),
            'avg_price_current': np.mean([t.get('price_per_credit', 200) for t in recent_transactions]) if recent_transactions else 200,
            'market_cap': sum(t.get('credit_amount', 0) * 200 for t in self.token_registry.values() if t.get('status') == 'active'),
            'retirement_rate_30d': self._calculate_recent_retirement_rate(30)
        }
        
        # Latest activities feed
        activity_feed = []
        for transaction in sorted(recent_transactions, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]:
            activity_feed.append({
                'timestamp': transaction.get('timestamp'),
                'type': 'trade',
                'description': f"{transaction.get('credits_sold', 0)} tCO₂e traded for ₹{transaction.get('total_value', 0):,.0f}",
                'project': transaction.get('project_name', 'Unknown Project'),
                'buyer': transaction.get('buyer_name', 'Anonymous Buyer')
            })
        
        # Add recent retirements
        recent_retirements = [
            t for t in self.token_registry.values() 
            if t.get('status') == 'retired' and 
            datetime.fromisoformat(t.get('retirement_date', current_time.isoformat())) > current_time - timedelta(hours=24)
        ]
        
        for retirement in recent_retirements[:5]:
            activity_feed.append({
                'timestamp': retirement.get('retirement_date'),
                'type': 'retirement',
                'description': f"{retirement.get('credit_amount', 0)} tCO₂e permanently retired",
                'project': retirement.get('project_name', 'Unknown Project'),
                'retired_by': retirement.get('retired_by', 'Anonymous Entity')
            })
        
        # Sort activity feed by timestamp
        activity_feed.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'dashboard_id': f'LIVE_DASH_{current_time.strftime("%Y%m%d_%H%M%S")}',
            'last_updated': current_time.isoformat(),
            'live_metrics': live_metrics,
            'activity_feed': activity_feed[:15],
            'price_trend_24h': self._calculate_price_trend(),
            'top_projects_by_volume': self._get_top_projects_by_volume(),
            'market_health_indicators': self._assess_market_health()
        }
    
    def _generate_sample_token_data(self):
        """Generate sample token data for demonstration"""
        
        ecosystems = ['mangrove_forest', 'seagrass_beds', 'salt_marshes', 'coastal_wetlands']
        ngos = [f'NGO{2000 + i}' for i in range(10)]
        industries = [f'IND{3000 + i}' for i in range(15)]
        
        # Generate tokens
        for i in range(50):
            token_id = f'BC{100000 + i}'
            project_id = f'PROJ{1001 + (i % 20)}'
            ngo_id = random.choice(ngos)
            
            token = {
                'token_id': token_id,
                'project_id': project_id,
                'project_name': f'Blue Carbon Project {project_id[-3:]}',
                'creator_ngo': ngo_id,
                'ecosystem_type': random.choice(ecosystems),
                'credit_amount': random.uniform(5, 50),
                'vintage_year': random.choice([2022, 2023, 2024]),
                'mint_date': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                'current_owner': random.choice([ngo_id] + industries + ['marketplace']),
                'status': random.choice(['active'] * 7 + ['retired'] * 3),  # 70% active, 30% retired
                'verification_standard': 'BlueCarbon MRV Protocol v2.1'
            }
            
            if token['status'] == 'retired':
                token['retired_by'] = random.choice(industries)
                token['retirement_date'] = (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
            
            self.token_registry[token_id] = token
        
        # Generate transactions
        for i in range(30):
            transaction = {
                'id': f'TXN{100000 + i}',
                'token_id': random.choice(list(self.token_registry.keys())),
                'project_id': f'PROJ{1001 + (i % 20)}',
                'project_name': f'Blue Carbon Project {(1001 + (i % 20)) % 1000}',
                'seller_id': random.choice(ngos),
                'buyer_id': random.choice(industries),
                'buyer_name': f'EcoTech Industries {random.randint(1, 10)}',
                'credits_sold': random.uniform(5, 25),
                'price_per_credit': random.uniform(180, 280),
                'total_value': 0,  # Will be calculated
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                'status': random.choice(['Completed'] * 8 + ['Pending', 'Failed']),
                'blockchain_hash': f'0x{random.randint(1000000000000000, 9999999999999999):016x}'
            }
            transaction['total_value'] = transaction['credits_sold'] * transaction['price_per_credit']
            
            self.transaction_history.append(transaction)
    
    def _calculate_recent_retirement_rate(self, days):
        """Calculate retirement rate for recent period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_retirements = [
            t for t in self.token_registry.values()
            if t.get('status') == 'retired' and
            datetime.fromisoformat(t.get('retirement_date', datetime.now().isoformat())) > cutoff_date
        ]
        
        total_recent_credits = sum(t.get('credit_amount', 0) for t in recent_retirements)
        total_active_credits = sum(t.get('credit_amount', 0) for t in self.token_registry.values() if t.get('status') == 'active')
        
        return (total_recent_credits / max(total_active_credits + total_recent_credits, 1)) * 100
    
    def _calculate_price_trend(self):
        """Calculate 24-hour price trend"""
        recent_transactions = [
            t for t in self.transaction_history
            if datetime.fromisoformat(t.get('timestamp', datetime.now().isoformat())) > datetime.now() - timedelta(hours=24)
            and t.get('status') == 'Completed'
        ]
        
        if len(recent_transactions) < 2:
            return {'trend': 'stable', 'change_percent': 0}
        
        # Sort by timestamp
        recent_transactions.sort(key=lambda x: x.get('timestamp', ''))
        
        # Get first half and second half average prices
        mid_point = len(recent_transactions) // 2
        early_avg = np.mean([t.get('price_per_credit', 200) for t in recent_transactions[:mid_point]])
        late_avg = np.mean([t.get('price_per_credit', 200) for t in recent_transactions[mid_point:]])
        
        change_percent = ((late_avg - early_avg) / early_avg) * 100
        
        if change_percent > 2:
            trend = 'rising'
        elif change_percent < -2:
            trend = 'falling'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change_percent': change_percent,
            'current_price': late_avg
        }
    
    def _get_top_projects_by_volume(self):
        """Get top projects by trading volume"""
        project_volumes = {}
        
        for transaction in self.transaction_history:
            if transaction.get('status') == 'Completed':
                project_id = transaction.get('project_id')
                if project_id not in project_volumes:
                    project_volumes[project_id] = {
                        'project_name': transaction.get('project_name'),
                        'volume': 0,
                        'transaction_count': 0
                    }
                project_volumes[project_id]['volume'] += transaction.get('total_value', 0)
                project_volumes[project_id]['transaction_count'] += 1
        
        # Sort by volume and return top 5
        top_projects = sorted(project_volumes.items(), key=lambda x: x[1]['volume'], reverse=True)[:5]
        
        return [
            {
                'project_id': proj_id,
                'project_name': data['project_name'],
                'volume': data['volume'],
                'transaction_count': data['transaction_count']
            }
            for proj_id, data in top_projects
        ]
    
    def _assess_market_health(self):
        """Assess overall market health indicators"""
        
        total_tokens = len(self.token_registry)
        active_tokens = len([t for t in self.token_registry.values() if t.get('status') == 'active'])
        recent_transactions = len([
            t for t in self.transaction_history
            if datetime.fromisoformat(t.get('timestamp', datetime.now().isoformat())) > datetime.now() - timedelta(days=7)
        ])
        
        # Calculate health scores (0-100)
        liquidity_score = min((active_tokens / max(total_tokens, 1)) * 100, 100)
        activity_score = min((recent_transactions / 7) * 20, 100)  # Target: 5 transactions per day
        diversity_score = min(len(set(t.get('ecosystem_type') for t in self.token_registry.values())) * 25, 100)
        
        overall_health = (liquidity_score + activity_score + diversity_score) / 3
        
        return {
            'overall_health_score': overall_health,
            'liquidity_score': liquidity_score,
            'activity_score': activity_score,
            'diversity_score': diversity_score,
            'health_rating': 'excellent' if overall_health > 80 else 'good' if overall_health > 60 else 'moderate' if overall_health > 40 else 'poor'
        }

# Global token visualization engine instance
token_viz_engine = TokenVisualizationEngine()