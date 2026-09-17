from flask_migrate import Migrate
from pirddiiqlab.models import InventoryItem, InventoryLot, StockMovement

migrate = Migrate()

def create_app(db_path=None):
    app = Flask(__name__)
    # Existing configuration...
    db.init_app(app)
    migrate.init_app(app, db)
    register_routes(app)
    return app
