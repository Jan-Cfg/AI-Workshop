package com.coforgeaiworkshop.session;

import java.util.List;

import com.coforgeaiworkshop.model.AiMessage;

public interface SessionStore {

	/** 
	 * Gets all the messages from the conversation
	 * 
	 * */
	public List<AiMessage> getAllMessages(String sessionId);
	
	/** 
	 * Gets the recent messages from the conversation
	 * 
	 * */
	public List<AiMessage> getRecentMessages(String sessionId);
	
	public void addMessage(String sessionId, AiMessage message);
	
	public boolean sessionExists(String sessionId);
	
	public void clearSession(String sessionId);
}
