# External Packages
from flask import Flask

# Internal Files
from .extensions import db
from .views import mainRoutes   # This prevents circular imports


app = Flask(__name__, template_folder='./templates')

app.config.from_pyfile('../settings.py')
app.secret_key = "ClfroxI$uFUH-sT=@Wiw"

db.init_app(app)
db.create_all(app=app)

app.register_blueprint(mainRoutes)

