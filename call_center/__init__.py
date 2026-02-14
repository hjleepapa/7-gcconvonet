"""
Call Center Module with SIP Phone Integration
Supports ACD features and SIP-based call handling
"""

from flask import Blueprint

call_center_bp = Blueprint('call_center', __name__, 
                          template_folder='templates',
                          static_folder='static',
                          static_url_path='/static',
                          url_prefix='/call-center')

from . import routes

