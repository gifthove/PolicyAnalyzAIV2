from __future__ import annotations
import logging

from openai import AzureOpenAI

import app.config as config

logger = logging.getLogger(__name__)

_BATCH_SIZE = 16

# This service provides utilities for generating embeddings for a list of input texts using the Azure OpenAI service. 
# It batches the input texts to stay within rate limits and returns a list of embedding vectors corresponding
# to each input text.
def _client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
    )

# This function takes a list of input texts and returns a list of embedding vectors, one for each input text. 
# It batches the input texts to ensure that the number of requests to the Azure OpenAI service stays within rate limits. The function uses the specified embedding model for generating the embeddings.
def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Return one embedding vector per input text, batching calls to stay within rate limits."""
    if not texts:
        return []
    client = _client()
    results: list[list[float]] = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i : i + _BATCH_SIZE]
        response = client.embeddings.create(
            model=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input=batch,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        results.extend(item.embedding for item in ordered)
        logger.debug("Embedded batch offset=%d size=%d", i, len(batch))
    return results
