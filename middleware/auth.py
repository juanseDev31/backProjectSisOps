from functools import wraps
from flask import request, jsonify
import jwt
from config import Config
from services.supabase import supabase

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            
            current_user = supabase.table('users').select('*').eq('id', data['user_id']).execute()
            
            if not current_user.data:
                return jsonify({'error': 'Usuario no encontrado'}), 401
            
            kwargs['current_user'] = current_user.data[0]
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    return decorated