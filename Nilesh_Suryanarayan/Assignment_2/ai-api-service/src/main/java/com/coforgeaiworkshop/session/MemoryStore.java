package com.coforgeaiworkshop.session;

import java.util.List;
import java.util.Map;

public interface MemoryStore {

	void saveMemory(String sessionId, String content, Map<String, Object> metadata);
	
	void saveMemory(String sessionId, String content);
	
    List<String> searchRelevantMemories(String sessionId, String query, int topK);
    
    void clearBySession(String sessionId);
	
}
