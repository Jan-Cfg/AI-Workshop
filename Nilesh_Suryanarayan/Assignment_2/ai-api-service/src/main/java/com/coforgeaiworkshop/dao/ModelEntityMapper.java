package com.coforgeaiworkshop.dao;

import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

import org.springframework.stereotype.Repository;

import com.coforgeaiworkshop.AiRole;
import com.coforgeaiworkshop.jpa.entity.ChatMessage;
import com.coforgeaiworkshop.jpa.entity.ChatSummary;
import com.coforgeaiworkshop.model.AiMessage;

@Repository
public class ModelEntityMapper {

	public ChatMessage mapAiMessageToChatMessage(AiMessage aiMessage, String sessionId) {
		ChatMessage chatMessage = new ChatMessage();
		
		chatMessage.setContent(aiMessage.getContent());
		chatMessage.setCreatedAt(aiMessage.getCreateUpdateTimestamp());
		chatMessage.setRole(aiMessage.getRole().toString());
		chatMessage.setSessionId(sessionId);
		
		return chatMessage;
	}
	
	public AiMessage mapChatMessageToAiMessage(ChatMessage chatMessage) {
		AiMessage aiMessage = new AiMessage();
		
		aiMessage.setContent(chatMessage.getContent());
		aiMessage.setCreateUpdateTimestamp(chatMessage.getCreatedAt());
		aiMessage.setRole(AiRole.valueOf(chatMessage.getRole()));
		
		return aiMessage;
	}
	
	public List<AiMessage> mapToListAiMessage(List<ChatMessage> chatMessages) {
		List<AiMessage> aiMessages = new CopyOnWriteArrayList<>();
		for(ChatMessage chatMessage: chatMessages) {
			aiMessages.add(mapChatMessageToAiMessage(chatMessage));
		}
		return aiMessages;
	}
	
	public ChatSummary mapChatSummary(String summary, String sessionId) {
		ChatSummary chatSummary = new ChatSummary();
		chatSummary.setSessionId(sessionId);
		chatSummary.setSummary(summary);
		chatSummary.setUpdatedAt(LocalDateTime.now());
		return chatSummary;
	}
}
