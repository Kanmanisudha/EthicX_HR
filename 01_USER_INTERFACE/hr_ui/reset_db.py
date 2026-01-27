import os
import sys

# Ensure the script can find the app and config files in the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
except ImportError:
    print("❌ Error: Could not find app.py. Make sure this script is in the same folder as your UI app.")
    sys.exit(1)

def perform_reset():
    print("⏳ Initializing EthicX-HR Database Reset...")

    with app.app_context():
        try:
            # 1. Clear existing data to prevent schema mismatch errors
            db.drop_all()
            print("🗑️  Old database tables deleted (Schema cleared).")

            # 2. Re-create tables with the latest Candidate and User models
            db.create_all()
            print("✨ New database tables created with latest columns (match_confidence, etc.).")
            
            # 3. Create a clean Admin user for the new DB
            from app import User
            admin = User(username='admin')
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()
            print("👤 Default Admin created: [User: admin / Pass: password]")

        except Exception as e:
            print(f"❌ Reset failed: {e}")

if __name__ == "__main__":
    perform_reset()
    print("\n✅ Database is now synchronized with your 6-Tier logic.")
    print("🚀 You can now run 'python app.py' to start the UI.")