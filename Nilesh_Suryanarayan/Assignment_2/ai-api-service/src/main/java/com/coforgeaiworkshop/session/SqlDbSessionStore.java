package com.coforgeaiworkshop.session;

import java.util.List;

import com.coforgeaiworkshop.model.AiMessage;

public class SqlDbSessionStore implements SessionStore {

	@Override
	public void addMessage(String sessionId, AiMessage message) {
		// TODO Auto-generated method stub

	}

	@Override
	public boolean sessionExists(String sessionId) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public void clearSession(String sessionId) {
		// TODO Auto-generated method stub

	}

	@Override
	public List<AiMessage> getAllMessages(String sessionId) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public List<AiMessage> getRecentMessages(String sessionId) {
		// TODO Auto-generated method stub
		return null;
	}

}
