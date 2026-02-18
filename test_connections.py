#!/usr/bin/env python3
"""
Test script to verify all connections are working
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    print("Testing imports...")
    
    try:
        from database.connection import Base, engine, SessionLocal, get_db
        print("✅ Database connection imports OK")
    except Exception as e:
        print(f"❌ Database connection imports FAILED: {e}")
        return False
    
    try:
        from database.models import Title, BulkUploadRun
        print("✅ Database models imports OK")
    except Exception as e:
        print(f"❌ Database models imports FAILED: {e}")
        return False
    
    try:
        from backend.services.title_service import save_title, check_duplicate
        print("✅ Title service imports OK")
    except Exception as e:
        print(f"❌ Title service imports FAILED: {e}")
        return False
    
    try:
        from backend.services.embedding_service import get_embedding
        print("✅ Embedding service imports OK")
    except Exception as e:
        print(f"❌ Embedding service imports FAILED: {e}")
        return False
    
    try:
        from backend.routes.title_routes import router as title_router
        from backend.routes.excel_routes import router as excel_router
        from backend.routes.admin_routes import router as admin_router
        print("✅ All routes imports OK")
    except Exception as e:
        print(f"❌ Routes imports FAILED: {e}")
        return False
    
    return True

def test_database():
    print("\nTesting database connection...")
    
    try:
        from database.connection import Base, engine
        from database.models import Title, BulkUploadRun
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test session
        from database.connection import SessionLocal
        db = SessionLocal()
        count = db.query(Title).count()
        db.close()
        print(f"✅ Database query successful (found {count} titles)")
        
        return True
    except Exception as e:
        print(f"❌ Database test FAILED: {e}")
        return False

def test_directories():
    print("\nTesting directory structure...")
    
    required_dirs = [
        Path("temp/uploads"),
        Path("database"),
        Path("backend"),
        Path("frontend")
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            all_exist = False
    
    return all_exist

def test_env():
    print("\nTesting environment configuration...")
    
    from pathlib import Path
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file exists")
        with open(env_file) as f:
            content = f.read()
            if "DATABASE_URL" in content:
                print("✅ DATABASE_URL configured")
            else:
                print("⚠️  DATABASE_URL not found in .env")
        return True
    else:
        print("❌ .env file missing")
        return False

def main():
    print("=" * 60)
    print("Clearoid Connection Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Directories", test_directories()))
    results.append(("Environment", test_env()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! System is ready.")
        print("\nStart the server with:")
        print("  ./start.sh (Linux/Mac)")
        print("  start.bat (Windows)")
        print("\nOr manually:")
        print("  cd backend && uvicorn main:app --reload")
    else:
        print("⚠️  Some tests failed. Check errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
