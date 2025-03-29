from flask import Flask
from flask_migrate import Migrate
from app.models import db
from app.routes import main_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notesync.db'

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
