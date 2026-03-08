import httpx
from app.config import settings


async def download_file(file_path: str) -> bytes:
    """
    Generate a signed URL from Supabase and stream download the file.
    No /tmp storage needed.
    """
    from supabase import create_client

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    # Generate signed URL (valid for 60 seconds)
    response = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).create_signed_url(
        file_path, expires_in=60
    )
    signed_url = response.get("signedURL") or response.get("signedUrl")

    if not signed_url:
        raise ValueError(f"Could not generate signed URL for: {file_path}")

    # Stream download into memory
    async with httpx.AsyncClient() as client:
        r = await client.get(signed_url)
        r.raise_for_status()
        return r.content