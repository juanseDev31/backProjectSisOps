from api.auth.routes import auth_bp
from api.categorias.routes import categories_bp
from api.products.routes import products_bp
from api.orders.routes import orders_bp
from api.upload.routes import upload_bp

def register_blueprints(app):
    """Registra todos los blueprints en la aplicación Flask"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(upload_bp)