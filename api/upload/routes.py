from flask import Blueprint, request, jsonify
from services.supabase import supabase
from middleware.auth import token_required
import uuid

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/image', methods=['POST'])
@token_required
def upload_image(current_user):
    if 'image' not in request.files:
        return jsonify({'error': 'No se envió imagen'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Tipo de archivo no permitido',
            'allowed': list(ALLOWED_EXTENSIONS)
        }), 400
    
    # Generar nombre único
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{current_user['id']}/{uuid.uuid4()}.{ext}"
    
    try:
        # Leer archivo
        file_bytes = file.read()
        
        # Subir a Supabase Storage
        supabase.storage.from_('product-images').upload(filename, file_bytes)
        
        # Obtener URL pública
        public_url = supabase.storage.from_('product-images').get_public_url(filename)
        
        return jsonify({
            'message': 'Imagen subida exitosamente',
            'image_url': public_url
        })
    
    except Exception as e:
        return jsonify({'error': f'Error al subir imagen: {str(e)}'}), 500


@upload_bp.route('/image/<path:filename>', methods=['DELETE'])
@token_required
def delete_image(current_user, filename):
    try:
        # Verificar que el archivo pertenece al usuario
        if not filename.startswith(current_user['id']):
            return jsonify({'error': 'No autorizado'}), 403
        
        supabase.storage.from_('product-images').remove([filename])
        
        return jsonify({'message': 'Imagen eliminada'})
    
    except Exception as e:
        return jsonify({'error': f'Error al eliminar imagen: {str(e)}'}), 500