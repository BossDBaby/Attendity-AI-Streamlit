from config.database import db_manager
from utils.data_migration import migrate_json_to_database

def setup_application():
    """Initialize the application with database"""
    print("Setting up Attendity database...")
    
    # Initialize database tables
    db_manager.init_db()
    print("✅ Database tables created")
    
    # Migrate existing data
    try:
        migrate_json_to_database()
        print("✅ Data migration completed")
    except Exception as e:
        print(f"⚠️ Migration skipped: {e}")
    
    print("🎉 Setup completed! You can now run your Streamlit app.")

if __name__ == "__main__":
    setup_application()
