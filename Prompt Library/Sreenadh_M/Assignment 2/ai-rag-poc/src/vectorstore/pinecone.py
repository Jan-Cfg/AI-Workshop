class PineconeVectorStore:
    def __init__(self, api_key, environment):
        import pinecone
        self.api_key = api_key
        self.environment = environment
        pinecone.init(api_key=self.api_key, environment=self.environment)
        self.index = None

    def create_index(self, index_name, dimension):
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(index_name, dimension=dimension)
        self.index = pinecone.Index(index_name)

    def upsert(self, vectors):
        if self.index is not None:
            self.index.upsert(vectors)

    def query(self, vector, top_k=5):
        if self.index is not None:
            return self.index.query(vector, top_k=top_k)

    def delete(self, ids):
        if self.index is not None:
            self.index.delete(ids)

    def close(self):
        if self.index is not None:
            self.index.close()