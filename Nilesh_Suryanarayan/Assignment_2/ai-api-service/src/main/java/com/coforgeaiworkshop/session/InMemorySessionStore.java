package com.coforgeaiworkshop.session;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;

import com.coforgeaiworkshop.model.AiMessage;

@Component
public class InMemorySessionStore implements SessionStore {

	private final Map<String, List<AiMessage>> storedSessions = new ConcurrentHashMap<>();

	@Override
	public List<AiMessage> getMessages(String sessionId) {
		return storedSessions.computeIfAbsent(sessionId, k -> new ArrayList<AiMessage>());
	}

	@Override
	public void addMessage(String sessionId, AiMessage message) {
		storedSessions.computeIfAbsent(sessionId, k -> new ArrayList<AiMessage>()).add(message);
	}

	@Override
	public boolean sessionExists(String sessionId) {
		return storedSessions.containsKey(sessionId);
	}

	@Override
	public void clearSession(String sessionId) {
		storedSessions.remove(sessionId);
	}
	
}
