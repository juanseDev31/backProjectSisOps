from flask import Blueprint, jsonify
from services.supabase import supabase

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@categories_bp.route('', methods=['GET'])
def get_categories():
    result = supabase.table('categories').select('*').execute()
    return jsonify(result.data)


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    result = supabase.table('categories').select('*').eq('id', category_id).execute()
    
    if not result.data:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    
    return jsonify(result.data[0])