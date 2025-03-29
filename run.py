from flask import Flask
from flask_migrate import Migrate
from app.models import db
from app.routes import main_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
