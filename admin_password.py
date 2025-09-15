from flask import Blueprint, request, jsonify, session
from src.models.admin import Admin
from src.models.user import db

admin_password_bp = Blueprint('admin_password', __name__)

@admin_password_bp.route('/admin/change-password', methods=['POST'])
def change_password():
    """Change admin password"""
    try:
        # Check authentication
        if 'admin_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Get current admin
        admin = Admin.query.get(session['admin_id'])
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        
        # Verify current password
        if not admin.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        admin.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

