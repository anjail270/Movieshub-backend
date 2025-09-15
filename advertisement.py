from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.advertisement import Advertisement, AdClick
from datetime import datetime

advertisement_bp = Blueprint('advertisement', __name__)

@advertisement_bp.route('/api/ads/<position>', methods=['GET'])
def get_ads_by_position(position):
    """Get active advertisements for a specific position"""
    try:
        ads = Advertisement.query.filter_by(
            position=position,
            is_active=True
        ).all()
        
        # Filter by date and return only currently active ads
        active_ads = []
        for ad in ads:
            if ad.is_currently_active():
                # Increment impression count
                ad.increment_impressions()
                active_ads.append(ad.to_dict())
        
        return jsonify({
            'success': True,
            'ads': active_ads
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advertisement_bp.route('/api/ads/click/<int:ad_id>', methods=['POST'])
def track_ad_click(ad_id):
    """Track advertisement click"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)
        
        # Increment click count
        ad.increment_clicks()
        
        # Record click details
        click_record = AdClick(
            advertisement_id=ad_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(click_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'redirect_url': ad.click_url
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advertisement_bp.route('/api/admin/ads', methods=['GET'])
def get_all_ads():
    """Get all advertisements for admin panel"""
    try:
        ads = Advertisement.query.order_by(Advertisement.created_at.desc()).all()
        return jsonify({
            'success': True,
            'ads': [ad.to_dict() for ad in ads]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advertisement_bp.route('/api/admin/ads', methods=['POST'])
def create_advertisement():
    """Create new advertisement"""
    try:
        data = request.get_json()
        
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if data.get('start_date'):
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        
        if data.get('end_date'):
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        ad = Advertisement(
            title=data['title'],
            ad_type=data['ad_type'],
            position=data['position'],
            content=data['content'],
            image_url=data.get('image_url'),
            click_url=data.get('click_url'),
            is_active=data.get('is_active', True),
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(ad)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Advertisement created successfully',
            'ad': ad.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advertisement_bp.route('/api/admin/ads/<int:ad_id>', methods=['PUT'])
def update_advertisement(ad_id):
    """Update advertisement"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)
        data = request.get_json()
        
        # Update fields
        ad.title = data.get('title', ad.title)
        ad.ad_type = data.get('ad_type', ad.ad_type)
        ad.position = data.get('position', ad.position)
        ad.content = data.get('content', ad.content)
        ad.image_url = data.get('image_url', ad.image_url)
        ad.click_url = data.get('click_url', ad.click_url)
        ad.is_active = data.get('is_active', ad.is_active)
        
        # Update dates if provided
        if data.get('start_date'):
            ad.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        
        if data.get('end_date'):
            ad.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Advertisement updated successfully',
            'ad': ad.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advertisement_bp.route('/api/admin/ads/<int:ad_id>', methods=['DELETE'])
def delete_advertisement(ad_id):
    """Delete advertisement"""
    try:
        ad = Advertisement.query.get_or_404(ad_id)
        db.session.delete(ad)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Advertisement deleted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advertisement_bp.route('/api/admin/ads/analytics', methods=['GET'])
def get_ad_analytics():
    """Get advertisement analytics"""
    try:
        ads = Advertisement.query.all()
        
        total_impressions = sum(ad.impressions for ad in ads)
        total_clicks = sum(ad.clicks for ad in ads)
        average_ctr = sum(ad.get_ctr() for ad in ads) / len(ads) if ads else 0
        
        analytics = {
            'total_ads': len(ads),
            'active_ads': len([ad for ad in ads if ad.is_currently_active()]),
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'average_ctr': round(average_ctr, 2),
            'ads_performance': [
                {
                    'id': ad.id,
                    'title': ad.title,
                    'impressions': ad.impressions,
                    'clicks': ad.clicks,
                    'ctr': ad.get_ctr()
                }
                for ad in ads
            ]
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

