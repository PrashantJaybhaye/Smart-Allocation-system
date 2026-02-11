from app import app, db
from models import SystemConfig
from sqlalchemy.exc import IntegrityError

with app.app_context():
    db.create_all()
    # Use a safe insert to avoid races
    try:
        if not SystemConfig.query.filter_by(key="allow_repref").first():
            db.session.add(SystemConfig(key="allow_repref", value="false"))
            db.session.commit()
            print("Initialized default config.")
    except IntegrityError:
        db.session.rollback()
        print("Config already exists or race occurred.")
    
    print("Database and Config check completed successfully!")
