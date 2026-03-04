from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase PostgreSQL connection string
    # Format: postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
    DATABASE_URL: str = ""
# postgresql+psycopg2://postgres.xotqfjonlzwnysjwreag:[Infraliti-AI]@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require
    # JWT settings
    SECRET_KEY: str = "b484160e52f2276aa73f2b426af32470afce7d4f8b85a40a5603541d4263ff43"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App settings
    APP_NAME: str = "Jaarvish API"
    DEBUG: bool = False

    # Supabase Storage settings
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET_NAME: str = "file-upload"
    
    # File upload settings
    MAX_FILE_SIZE_MB: int = 50  # Maximum file size in megabytes
    ALLOWED_EXTENSIONS: list[str] = [
        ".txt", ".pdf", ".docx", ".csv", ".xlsx", ".pptx", ".md"
    ]
    ALLOWED_MIME_TYPES: list[str] = [
        "text/plain",
        "text/markdown",
        "text/csv",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()