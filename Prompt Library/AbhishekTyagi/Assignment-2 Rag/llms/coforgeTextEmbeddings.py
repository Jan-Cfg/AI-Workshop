from langchain_core.embeddings import Embeddings
from typing import List, Optional
import requests
import os
import time
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv(override=True)


class CustomEmbeddings(Embeddings):
    """
    Custom Embeddings wrapper for Coforge Embedding API.

    API behavior:
    - Returns ONE flat embedding vector (List[float]) per request
    - Even if multiple texts are supplied

    LangChain expectation:
    - embed_query     -> List[float]
    - embed_documents -> List[List[float]]
    """

    def __init__(self):
        # ✅ Core configuration
        self.dimensions: int = 736
        self.model_name: str = os.getenv("EMBED_MODEL", "coforge-text-embedding")

        self.endpoint_url: str = os.environ["Emb_URL"]
        self.api_key: str = os.environ["QAG_API_KEY"]

        self.headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }

        # Print config ONCE so you know exactly what is being used
        self._print_config()

    # --------------------------------------------------
    # Debug / visibility helpers
    # --------------------------------------------------
    def _print_config(self):
        masked_key = self.api_key[:4] + "****" + self.api_key[-4:]
        print("\nCustomEmbeddings initialized")
        print("--------------------------------------------------")
        print(f" Endpoint URL : {self.endpoint_url}")
        print(f" Model        : {self.model_name}")
        print(f" Dimensions   : {self.dimensions}")
        print(f" API Key      : {masked_key}")
        print("--------------------------------------------------\n")

    # --------------------------------------------------
    # Internal: embed ONE text
    # --------------------------------------------------
    def _embed_one(self, text: str) -> List[float]:
        payload = {
            "texts": [text],                 # API supports single embedding
            "dimensions": self.dimensions
        }

        print(f" Calling embedding API")
        print(f"    URL        : {self.endpoint_url}")
        print(f"    Model      : {self.model_name}")
        print(f"    Text chars : {len(text)}")

        start = time.time()

        response = requests.post(
            self.endpoint_url,
            headers=self.headers,
            json=payload,
            timeout=20
        )
        response.raise_for_status()

        duration = round(time.time() - start, 2)
        result = response.json()

        if "embeddings" not in result:
            raise ValueError(f"Invalid response format: {result}")

        embedding = result["embeddings"]

        if not isinstance(embedding, list):
            raise ValueError("Expected embedding as List[float]")

        if len(embedding) != self.dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.dimensions}, got {len(embedding)}"
            )

        print(f" Received embedding | time={duration}s | dim={len(embedding)}\n")

        #  Small delay to be safe with gateways / rate limits
        time.sleep(0.2)

        return embedding

    # --------------------------------------------------
    # LangChain required methods
    # --------------------------------------------------
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        print(f"📚 Embedding {len(texts)} documents...\n")

        vectors = []
        total = len(texts)

        for idx, text in enumerate(texts, start=1):
            print(f"🔹 Document {idx}/{total}")
            vec = self._embed_one(text)
            vectors.append(vec)

        print(" All documents embedded successfully\n")
        return vectors

    def embed_query(self, text: str) -> List[float]:
        print("Embedding query...\n")
        return self._embed_one(text)

