package com.coforgeaiworkshop.session;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Repository;

@Repository
public class PgVectorMemoryStore implements MemoryStore {

	private final VectorStore vectorStore;
	
	public PgVectorMemoryStore(VectorStore vectorStore) {
		this.vectorStore = vectorStore;
	}
	
	@Override
	public void saveMemory(String sessionId, String content, Map<String, Object> metadata) {
		Document document = new Document(content, Map.of("sessionId", sessionId));
		vectorStore.add(List.of(document));
	}

	@Override
	public List<String> searchRelevantMemories(String sessionId, String query, int topK) {
		SearchRequest request = SearchRequest.builder()
                .query(query)
                .topK(topK)
                .build();
		
		return vectorStore.similaritySearch(request)
				.stream()
				.filter(doc -> sessionId.equals(doc.getMetadata().get("sessionId")))
				.map(Document::getFormattedContent)
				.collect(Collectors.toList());
	}

	@Override
	public void saveMemory(String sessionId, String content) {
		Document document = new Document(
                content,
                Map.of("sessionId", sessionId)
        );

        vectorStore.add(List.of(document));
	}

	@Override
	public void clearBySession(String sessionId) {
		// TODO Auto-generated method stub
		
	}

}
