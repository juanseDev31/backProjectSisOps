from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from config import Config
from services.supabase import supabase
from middleware.auth import token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    required = ['email', 'password', 'full_name']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} es requerido'}), 400
    
    existing = supabase.table('users').select('id').eq('email', data['email']).execute()
    if existing.data:
        return jsonify({'error': 'El email ya está registrado'}), 400
    
    user_data = {
        'email': data['email'],
        'password_hash': generate_password_hash(data['password']),
        'full_name': data['full_name'],
        'phone': data.get('phone'),
        'address': data.get('address')
    }
    
    result = supabase.table('users').insert(user_data).execute()
    
    if result.data:
        user = result.data[0]
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, Config.SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name']
            }
        }), 201
    
    return jsonify({'error': 'Error al registrar usuario'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y password son requeridos'}), 400
    
    result = supabase.table('users').select('*').eq('email', data['email']).execute()
    
    if not result.data:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    user = result.data[0]
    
    if not check_password_hash(user['password_hash'], data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, Config.SECRET_KEY, algorithm="HS256")
    
    return jsonify({
        'message': 'Login exitoso',
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name']
        }
    })


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'id': current_user['id'],
        'email': current_user['email'],
        'full_name': current_user['full_name'],
        'phone': current_user['phone'],
        'address': current_user['address']
    })