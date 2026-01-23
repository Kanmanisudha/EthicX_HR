from app import app, db

print("⏳ Connecting to database...")

with app.app_context():
    # 1. Drop all existing tables (Delete old data)
    db.drop_all()
    print("🗑️  Old database tables deleted.")

    # 2. Create new tables (With the new 'match_confidence' column)
    db.create_all()
    print("✨ New database created successfully!")

print("✅ You can now restart 'app.py' and the error will be gone.")