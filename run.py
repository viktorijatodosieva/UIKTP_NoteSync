# from flask import Flask
# from flask_migrate import Migrate
# from app.models import db
# from app.routes import main_bp
# from config import Config
#
# app = Flask(__name__)
# app.config.from_object(Config)
#
# db.init_app(app)
# migrate = Migrate(app, db)
#
# app.register_blueprint(main_bp)
#
# if __name__ == '__main__':
#     app.run(debug=True)


from app import create_app
from app.extensions import db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=False)