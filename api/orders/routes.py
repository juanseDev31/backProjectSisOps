from flask import Blueprint, request, jsonify
from services.supabase import supabase
from middleware.auth import token_required

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@orders_bp.route('', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.json
    
    if not data.get('product_id'):
        return jsonify({'error': 'product_id es requerido'}), 400
    
    quantity = data.get('quantity', 1)
    
    # Obtener producto
    product = supabase.table('products').select('*').eq('id', data['product_id']).eq('is_active', True).execute()
    
    if not product.data:
        return jsonify({'error': 'Producto no encontrado o no disponible'}), 404
    
    product = product.data[0]
    
    # Verificar que no sea el mismo vendedor
    if product['seller_id'] == current_user['id']:
        return jsonify({'error': 'No puedes comprar tu propio producto'}), 400
    
    # Verificar stock
    if product['stock'] < quantity:
        return jsonify({
            'error': 'Stock insuficiente',
            'stock_disponible': product['stock']
        }), 400
    
    # Crear orden
    order_data = {
        'buyer_id': current_user['id'],
        'product_id': product['id'],
        'seller_id': product['seller_id'],
        'quantity': quantity,
        'unit_price': product['price'],
        'total_price': float(product['price']) * quantity,
        'color': product['color'],
        'size': product['size'],
        'status': 'completed'
    }
    
    order_result = supabase.table('orders').insert(order_data).execute()
    
    if not order_result.data:
        return jsonify({'error': 'Error al crear la orden'}), 500
    
    # Actualizar stock
    new_stock = product['stock'] - quantity
    supabase.table('products').update({'stock': new_stock}).eq('id', product['id']).execute()
    
    # Si stock llega a 0, desactivar producto
    if new_stock == 0:
        supabase.table('products').update({'is_active': False}).eq('id', product['id']).execute()
    
    order = order_result.data[0]
    
    return jsonify({
        'message': '¡Compra exitosa!',
        'order': {
            'id': order['id'],
            'product_name': product['name'],
            'color': order['color'],
            'size': order['size'],
            'quantity': order['quantity'],
            'total_price': order['total_price'],
            'fecha_hora': order['created_at']
        }
    }), 201


@orders_bp.route('/my-purchases', methods=['GET'])
@token_required
def get_my_purchases(current_user):
    result = supabase.table('orders').select(
        '*, products(name, image_url), users!orders_seller_id_fkey(full_name)'
    ).eq('buyer_id', current_user['id']).order('created_at', desc=True).execute()
    
    return jsonify(result.data)


@orders_bp.route('/my-sales', methods=['GET'])
@token_required
def get_my_sales(current_user):
    result = supabase.table('orders').select(
        '*, products(name, image_url), users!orders_buyer_id_fkey(full_name)'
    ).eq('seller_id', current_user['id']).order('created_at', desc=True).execute()
    
    return jsonify(result.data)


@orders_bp.route('/<order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    result = supabase.table('orders').select(
        '*, products(name, image_url, description)'
    ).eq('id', order_id).execute()
    
    if not result.data:
        return jsonify({'error': 'Orden no encontrada'}), 404
    
    order = result.data[0]
    
    # Verificar que el usuario sea comprador o vendedor
    if order['buyer_id'] != current_user['id'] and order['seller_id'] != current_user['id']:
        return jsonify({'error': 'No autorizado'}), 403
    
    return jsonify(order)