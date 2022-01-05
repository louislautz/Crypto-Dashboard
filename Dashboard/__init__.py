# External Packages
from flask import Flask, Blueprint

# Internal Files
from views import mainRoutes
from extensions import db


def create_app(config_file='settings.py'):
    app = Flask(__name__, template_folder='../templates')
    
    app.config.from_pyfile(config_file)

    db.init_app(app)

    app.register_blueprint(mainRoutes)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)