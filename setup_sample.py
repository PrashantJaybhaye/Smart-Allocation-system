from app import app, db
from models import Course

def setup():
    with app.app_context():
        courses = [
            Course(name="Artificial Intelligence", capacity=2, faculty_name="Dr. Smith"),
            Course(name="Cyber Security", capacity=2, faculty_name="Prof. Johnson"),
            Course(name="Data Science", capacity=3, faculty_name="Dr. Brown"),
            Course(name="Cloud Computing", capacity=2, faculty_name="Ms. Davis")
        ]
        for c in courses:
            if not Course.query.filter_by(name=c.name).first():
                db.session.add(c)
        db.session.commit()
        print("Sample courses added!")

if __name__ == "__main__":
    setup()
