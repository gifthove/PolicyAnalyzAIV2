from azure.storage.blob import BlobServiceClient, ContentSettings
from app.config import AZURE_BLOB_CONNECTION_STRING


def upload_blob(container: str, blob_name: str, data: bytes, content_type: str) -> str:
    client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
    blob_client = client.get_blob_client(container=container, blob=blob_name)
    blob_client.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )
    return blob_client.url
