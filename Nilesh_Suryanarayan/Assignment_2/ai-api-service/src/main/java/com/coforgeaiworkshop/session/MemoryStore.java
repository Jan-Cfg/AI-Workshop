package com.coforgeaiworkshop.session;

import java.util.List;
import java.util.Map;

public interface MemoryStore {

	public void saveMemory(String sessionId, String content, Map<String, Object> metadata);
	
    public List<String> searchRelevantMemories(String sessionId, String query, int topK);
    
    public void clearMemories(String sessionId);
	
}
