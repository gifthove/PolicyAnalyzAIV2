from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

import app.config as config

logger = logging.getLogger(__name__)


@dataclass
class IndexedChunk:
    id: str
    document_id: str
    source_name: Optional[str]
    policy_date: Optional[str]
    chunk_index: int
    chunk_text: str
    embedding: list[float]
    created_at: str


def _index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=config.AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(config.AZURE_SEARCH_KEY),
    )


def _search_client() -> SearchClient:
    return SearchClient(
        endpoint=config.AZURE_SEARCH_ENDPOINT,
        index_name=config.AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(config.AZURE_SEARCH_KEY),
    )


def ensure_index_exists() -> None:
    index = SearchIndex(
        name=config.AZURE_SEARCH_INDEX_NAME,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="document_id", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="source_name", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="policy_date", type=SearchFieldDataType.String, filterable=True, sortable=True),
            SimpleField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
            SearchableField(name="chunk_text", type=SearchFieldDataType.String),
            SimpleField(name="created_at", type=SearchFieldDataType.String),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=config.AZURE_OPENAI_EMBEDDING_DIMENSIONS,
                vector_search_profile_name="hnsw-profile",
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
            profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-algo")],
        ),
    )
    _index_client().create_or_update_index(index)
    logger.info("Search index ensured: %s", config.AZURE_SEARCH_INDEX_NAME)


def index_chunks(chunks: list[IndexedChunk]) -> int:
    if not chunks:
        return 0
    documents = [
        {
            "id": c.id,
            "document_id": c.document_id,
            "source_name": c.source_name,
            "policy_date": c.policy_date,
            "chunk_index": c.chunk_index,
            "chunk_text": c.chunk_text,
            "embedding": c.embedding,
            "created_at": c.created_at,
        }
        for c in chunks
    ]
    results = _search_client().upload_documents(documents=documents)
    succeeded = sum(1 for r in results if r.succeeded)
    logger.info("Indexed %d/%d chunks for document_id=%s", succeeded, len(chunks), chunks[0].document_id)
    return succeeded


def delete_document(document_id: str) -> None:
    client = _search_client()
    hits = client.search(search_text="*", filter=f"document_id eq '{document_id}'", select=["id"])
    to_delete = [{"id": r["id"]} for r in hits]
    if to_delete:
        client.delete_documents(documents=to_delete)
        logger.info("Deleted %d chunks for document_id=%s", len(to_delete), document_id)
