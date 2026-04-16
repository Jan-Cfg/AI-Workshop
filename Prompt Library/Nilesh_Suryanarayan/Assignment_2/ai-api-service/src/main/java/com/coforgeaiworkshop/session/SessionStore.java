package com.coforgeaiworkshop.session;

import java.util.List;

import com.coforgeaiworkshop.model.AiMessage;

public interface SessionStore {

	public List<AiMessage> getMessages(String sessionId);
	
	public void addMessage(String sessionId, AiMessage message);
	
	public boolean sessionExists(String sessionId);
	
	public void clearSession(String sessionId);
}
