from flask import Blueprint, request, jsonify
from services.supabase import supabase
from middleware.auth import token_required

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def get_products():
    query = supabase.table('products').select('*, categories(name), users(full_name)').eq('is_active', True)
    
    # Filtros opcionales
    category_id = request.args.get('category_id')
    if category_id:
        query = query.eq('category_id', category_id)
    
    min_price = request.args.get('min_price')
    if min_price:
        query = query.gte('price', min_price)
    
    max_price = request.args.get('max_price')
    if max_price:
        query = query.lte('price', max_price)
    
    size = request.args.get('size')
    if size:
        query = query.eq('size', size)
    
    color = request.args.get('color')
    if color:
        query = query.ilike('color', f'%{color}%')
    
    result = query.order('created_at', desc=True).execute()
    return jsonify(result.data)


@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    result = supabase.table('products').select('*, categories(name), users(full_name, email)').eq('id', product_id).execute()
    
    if not result.data:
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    return jsonify(result.data[0])


@products_bp.route('', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.json
    
    required = ['name', 'price', 'category_id', 'color', 'size']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} es requerido'}), 400
    
    # Validar que category_id sea válido (1-4)
    if data['category_id'] not in [1, 2, 3, 4]:
        return jsonify({'error': 'Categoría inválida. Debe ser 1-4'}), 400
    
    product_data = {
        'seller_id': current_user['id'],
        'category_id': data['category_id'],
        'name': data['name'],
        'description': data.get('description'),
        'price': data['price'],
        'image_url': data.get('image_url'),
        'color': data['color'],
        'size': data['size'],
        'stock': data.get('stock', 1)
    }
    
    result = supabase.table('products').insert(product_data).execute()
    
    if result.data:
        return jsonify({
            'message': 'Producto creado exitosamente',
            'product': result.data[0]
        }), 201
    
    return jsonify({'error': 'Error al crear producto'}), 500


@products_bp.route('/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    product = supabase.table('products').select('*').eq('id', product_id).eq('seller_id', current_user['id']).execute()
    
    if not product.data:
        return jsonify({'error': 'Producto no encontrado o no autorizado'}), 404
    
    data = request.json
    allowed_fields = ['name', 'description', 'price', 'image_url', 'color', 'size', 'stock', 'category_id', 'is_active']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if 'category_id' in update_data and update_data['category_id'] not in [1, 2, 3, 4]:
        return jsonify({'error': 'Categoría inválida. Debe ser 1-4'}), 400
    
    result = supabase.table('products').update(update_data).eq('id', product_id).execute()
    
    return jsonify({
        'message': 'Producto actualizado',
        'product': result.data[0]
    })


@products_bp.route('/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = supabase.table('products').select('*').eq('id', product_id).eq('seller_id', current_user['id']).execute()
    
    if not product.data:
        return jsonify({'error': 'Producto no encontrado o no autorizado'}), 404
    
    supabase.table('products').delete().eq('id', product_id).execute()
    
    return jsonify({'message': 'Producto eliminado'})


@products_bp.route('/my-products', methods=['GET'])
@token_required
def get_my_products(current_user):
    result = supabase.table('products').select('*, categories(name)').eq('seller_id', current_user['id']).order('created_at', desc=True).execute()
    return jsonify(result.data)