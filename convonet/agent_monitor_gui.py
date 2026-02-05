"""
Agent Monitor GUI - Flask routes and API endpoints
Provides web-based GUI for monitoring LLM agent interactions
"""

from flask import Blueprint, render_template, jsonify, request
from typing import Dict, List, Optional
import json

from .agent_monitor import get_agent_monitor, AgentInteraction

agent_monitor_bp = Blueprint('agent_monitor', __name__, url_prefix='/agent-monitor')


@agent_monitor_bp.route('/', strict_slashes=False)
@agent_monitor_bp.route('', strict_slashes=False)
def agent_monitor_dashboard():
    """Render the agent monitoring dashboard"""
    return render_template('agent_monitor_dashboard.html')


@agent_monitor_bp.route('/api/interactions')
def get_interactions():
    """Get recent agent interactions"""
    try:
        limit = int(request.args.get('limit', 50))
        provider = request.args.get('provider')
        agent_type = request.args.get('agent_type')  # Filter by domain: todo, mortgage, healthcare
        
        monitor = get_agent_monitor()
        
        if provider:
            interactions = monitor.get_interactions_by_provider(provider, limit=limit)
        else:
            interactions = monitor.get_recent_interactions(limit=limit)
        
        # Convert to dict format
        interactions_data = [interaction.to_dict() for interaction in interactions]
        
        # Filter by agent_type if specified
        if agent_type:
            interactions_data = [
                i for i in interactions_data 
                if i.get('metadata', {}).get('agent_type') == agent_type
            ]
        
        return jsonify({
            "success": True,
            "interactions": interactions_data,
            "count": len(interactions_data)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@agent_monitor_bp.route('/api/interaction/<request_id>')
def get_interaction(request_id: str):
    """Get a specific interaction by request ID"""
    try:
        monitor = get_agent_monitor()
        interaction = monitor.get_interaction(request_id)
        
        if interaction:
            return jsonify({
                "success": True,
                "interaction": interaction.to_dict()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Interaction not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@agent_monitor_bp.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        monitor = get_agent_monitor()
        stats = monitor.get_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

