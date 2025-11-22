from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from api import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Habilitar CORS
    CORS(app)
    
    # Registrar todos los blueprints
    register_blueprints(app)
    
    # Ruta principal
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            'message': 'API Marketplace de Ropa',
            'version': '1.0',
            'status': 'running',
            'endpoints': {
                'auth': {
                    'POST /api/auth/register': 'Registrar usuario',
                    'POST /api/auth/login': 'Iniciar sesión',
                    'GET /api/auth/me': 'Obtener usuario actual'
                },
                'categories': {
                    'GET /api/categories': 'Listar categorías',
                    'GET /api/categories/<id>': 'Obtener categoría'
                },
                'products': {
                    'GET /api/products': 'Listar productos',
                    'GET /api/products/<id>': 'Obtener producto',
                    'POST /api/products': 'Crear producto',
                    'PUT /api/products/<id>': 'Actualizar producto',
                    'DELETE /api/products/<id>': 'Eliminar producto',
                    'GET /api/products/my-products': 'Mis productos'
                },
                'orders': {
                    'POST /api/orders': 'Crear orden (comprar)',
                    'GET /api/orders/<id>': 'Obtener orden',
                    'GET /api/orders/my-purchases': 'Mis compras',
                    'GET /api/orders/my-sales': 'Mis ventas'
                },
                'upload': {
                    'POST /api/upload/image': 'Subir imagen'
                }
            }
        })
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)