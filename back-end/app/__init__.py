from flask import Flask

def create_app():
    app = Flask(__name__)

    # Configuration de base
    app.config['SECRET_KEY'] = 'secret_key_dev'

    # Importer et enregistrer les routes
    from .routes import main
    app.register_blueprint(main)

    return app
