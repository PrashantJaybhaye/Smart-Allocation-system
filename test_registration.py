from app import app, db
from models import User

with app.app_context():
    try:
        username = "testuser_debug"
        password = "testpassword"
        user_exists = User.query.filter_by(username=username).first()
        if not user_exists:
            new_user = User(username=username, role='student')
            new_user.password = password
            db.session.add(new_user)
            db.session.commit()
            print(f"User {username} created successfully!")
        else:
            print(f"User {username} already exists.")
    except Exception as e:
        print(f"Error: {e}")
