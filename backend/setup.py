"""
Setup script for the File Upload API.
Run this to configure your environment and install all dependencies.
"""

import os
import subprocess
import sys
from pathlib import Path


def print_step(message):
    """Print a formatted step message."""
    print(f"\n{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}\n")


def check_python_version():
    """Verify Python version is compatible."""
    print_step("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")


def create_env_file():
    """Create .env file from example if it doesn't exist."""
    print_step("Setting up environment file...")
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return
    
    # Create .env file with template
    env_content = """# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres.your-project-ref:your-password@aws-0-region.pooler.supabase.com:6543/postgres?sslmode=require

# JWT Configuration
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
APP_NAME=Jaarvish API
DEBUG=False

# Supabase Storage Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
SUPABASE_BUCKET_NAME=file-upload

# File Upload Settings
MAX_FILE_SIZE_MB=50
"""
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("⚠️  IMPORTANT: Update .env with your actual Supabase credentials!")


def install_dependencies():
    """Install Python dependencies."""
    print_step("Installing Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def verify_imports():
    """Verify key imports are working."""
    print_step("Verifying installations...")
    
    packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "supabase",
        "filetype",
        "pydantic",
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - FAILED")


def print_next_steps():
    """Print instructions for next steps."""
    print_step("Setup Complete! Next Steps:")
    
    print("""
1. Configure Supabase:
   - Update .env file with your Supabase URL and API key
   - Create a bucket named 'file-upload' in Supabase Storage
   - Update DATABASE_URL with your Supabase PostgreSQL connection

2. Generate a secure JWT secret key:
   python -c "import secrets; print(secrets.token_hex(32))"
   
   Update SECRET_KEY in .env with the generated value

3. Start the development server:
   uvicorn app.main:app --reload

4. Access the API documentation:
   http://localhost:8000/docs

5. Test the file upload endpoints:
   - First register/login to get an access token
   - Use the token to upload files via /files/upload

📖 For detailed documentation, see FILE_UPLOAD_README.md

🔧 Troubleshooting:
   - If imports fail in VS Code, select the correct Python interpreter
   - Ensure you're using the virtual environment if created
   - Check that all environment variables are set in .env
""")


def main():
    """Main setup function."""
    print("\n🚀 Jaarvish Backend - File Upload API Setup")
    
    # Change to backend directory if not already there
    if Path("requirements.txt").exists():
        check_python_version()
        create_env_file()
        install_dependencies()
        verify_imports()
        print_next_steps()
    else:
        print("❌ Please run this script from the backend directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
