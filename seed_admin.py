import os
from app import app, db
from models import User, SystemConfig

with app.app_context():
    # Use environment provided password if available
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        print("Creating admin user...")
        admin = User(username='admin', role='admin')
        admin.password = admin_pass
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created with username 'admin' and password '{admin_pass}'")
    else:
        print("Admin user already exists. Updating password...")
        admin_user.password = admin_pass
        db.session.commit()
        print(f"Admin password updated to '{admin_pass}'")
        
    print("Seeding/Checking system configuration...")
    if not SystemConfig.query.filter_by(key='allow_repref').first():
        config = SystemConfig(key='allow_repref', value='false')
        db.session.add(config)
        db.session.commit()
        print("Default system configuration initialized.")
    
    print("Seeding completed successfully!")
