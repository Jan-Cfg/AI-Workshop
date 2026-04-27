package com.coforgeaiworkshop.session;

import static com.coforgeaiworkshop.AppConstants.MAX_LIMIT_FOR_RECENT_CHATS;
import static com.coforgeaiworkshop.AppConstants.SYSTEM_PROMPT;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;

import com.coforgeaiworkshop.AiRole;
import com.coforgeaiworkshop.model.AiMessage;

@Component
public class InMemorySessionStore implements SessionStore {

	private final Map<String, List<AiMessage>> storedSessions = new ConcurrentHashMap<>();

	@Override
	public List<AiMessage> getAllMessages(String sessionId) {
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

	@Override
	public List<AiMessage> getRecentMessages(String sessionId) {
		List<AiMessage> history = getAllMessages(sessionId);
		int start = Math.max(0, history.size() - MAX_LIMIT_FOR_RECENT_CHATS);
		
		List<AiMessage> recentHistory = history.subList(start, history.size());
		recentHistory.add(0, new AiMessage(AiRole.SYSTEM, SYSTEM_PROMPT, "", LocalDateTime.now()));
		return recentHistory;
	}
	
}
