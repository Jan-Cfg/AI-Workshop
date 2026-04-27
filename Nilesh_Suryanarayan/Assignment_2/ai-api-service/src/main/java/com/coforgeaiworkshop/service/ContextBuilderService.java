package com.coforgeaiworkshop.service;

import static com.coforgeaiworkshop.AppConstants.CHAT_SUMMARY_PROMPT;
import static com.coforgeaiworkshop.AppConstants.GLM_5_CLOUD_MODEL;
import static com.coforgeaiworkshop.AppConstants.MAX_LIMIT_FOR_RECENT_CHATS;
import static com.coforgeaiworkshop.AppConstants.STREAM_API_RES_TRUE;
import static com.coforgeaiworkshop.AppConstants.SYSTEM_PROMPT;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.coforgeaiworkshop.AiRole;
import com.coforgeaiworkshop.dao.ModelEntityMapper;
import com.coforgeaiworkshop.dto.AiConverseDTO;
import com.coforgeaiworkshop.jpa.entity.ChatMessage;
import com.coforgeaiworkshop.jpa.entity.ChatSummary;
import com.coforgeaiworkshop.jpa.repository.ChatMessageRepository;
import com.coforgeaiworkshop.jpa.repository.ChatSummaryRepository;
import com.coforgeaiworkshop.model.AiApiRequest;
import com.coforgeaiworkshop.model.AiMessage;
import com.coforgeaiworkshop.session.MemoryStore;
import com.coforgeaiworkshop.session.SessionStore;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class ContextBuilderService {
	
	@Autowired
	private SessionStore sessionStore;
	@Autowired
	private ModelEntityMapper modelEntityMapper;
	@Autowired
	private ChatMessageRepository messageRepository;
	@Autowired
	private ChatSummaryRepository summaryReposity;
	@Autowired
	private AiApiCaller aiApiCaller;
	@Autowired
	private MemoryStore vectorMemoryStore;
	

	/** 
	 * 
	 * 
	 * */
	public AiApiRequest buildRequest(AiConverseDTO aiConverseDto, String sessionId) {
		log.info("Building context for sessionId: {}", sessionId);
		List<AiMessage> recentHistroy = sessionStore.getRecentMessages(sessionId);
		List<AiMessage> messages = new ArrayList<AiMessage>();
		
		
		
		// Set system message
		AiMessage systemMessage = new AiMessage(AiRole.SYSTEM, SYSTEM_PROMPT, "", LocalDateTime.now());
//		messages.add(systemMessage);
		// Add session history
//		messages.addAll(recentHistroy);
		// Add Summary
		Optional<ChatSummary> optionalSummary = summaryReposity.findBySessionId(sessionId);
		ChatSummary summary = optionalSummary.orElseGet(() -> new ChatSummary());
//		messages.add(new AiMessage(AiRole.SYSTEM, "", summary.getSummary(), summary.getUpdatedAt()));
		// Add relevant memory
		List<String> relevantMemories = vectorMemoryStore.searchRelevantMemories(sessionId, aiConverseDto.getMessage(), 5);
		// Loop over the relevant memories and add to the prompt
//		for(String memory: relevantMemories) {
//			messages.add(new AiMessage(AiRole.SYSTEM, memory, "", null));
//		}
		// Add user input
		messages.add(new AiMessage(AiRole.USER, aiConverseDto.getMessage(), "", LocalDateTime.now()));
		
		
		
		
		/* Generate complete prompt with all recent chats, summary and relevant messages */
		String prompt = """
				SYSTEM:
				%s

				SUMMARY:
				%s

				RELEVANT MEMORY:
				%s

				RECENT CHAT:
				%s

				USER:
				%s
				""".formatted(
						systemMessage,
						summary, 
						String.join("\n", relevantMemories), 
						String.join("\n", recentHistroy.stream()
								.map(aiMessage -> aiMessage.getRole() + ": " + aiMessage.getContent())
								.collect(Collectors.toList())
								),
						aiConverseDto.getMessage()
						);
		
		messages.add(new AiMessage(AiRole.SYSTEM, prompt, "", LocalDateTime.now()));
		
		AiApiRequest aiApiRequest = new AiApiRequest(GLM_5_CLOUD_MODEL, messages, STREAM_API_RES_TRUE);
		
		return aiApiRequest;
	}
	
	/** 
	 * 
	 * 
	 * */
	public AiApiRequest buildRequest(List<ChatMessage> allMessages) {
		List<AiMessage> messages = new ArrayList<AiMessage>();
		AiMessage systemMessage = new AiMessage(AiRole.SYSTEM, SYSTEM_PROMPT, "", LocalDateTime.now());
		messages.add(systemMessage);
		// Add all messages
		messages.addAll(modelEntityMapper.mapToListAiMessage(allMessages));
		// Add summarization prompt
		messages.add(new AiMessage(AiRole.USER, CHAT_SUMMARY_PROMPT, "", LocalDateTime.now()));
		AiApiRequest aiApiRequest = new AiApiRequest(GLM_5_CLOUD_MODEL, messages, STREAM_API_RES_TRUE);
		
		return aiApiRequest;
	}
	
	/** 
	 * @param sessionId
	 * @param message of type {@link AiMessage}
	 * 
	 * 
	 * */
	public void addMessage(String sessionId, AiMessage reqMessage, AiMessage resMessage) {
		/* 
		 * STEP 1 : Check if the number of messages related to the session exceeds Recent chat threshold
		 * STEP 2 : NO  - store the message normally, SQL execution
		 * STEP 3 : YES
		 *     STEP 3.1 : Add message in Vector Database - map by sessionId
		 *     STEP 3.2 : Summarization - If summary don't exist, summarize the chat
		 *     STEP 3.3 : Store only the new message with the summary
		 * 
		 * */
		log.info("Inside add message with sessionId: {}", sessionId);
		ChatMessage reqChatMessage = modelEntityMapper.mapAiMessageToChatMessage(reqMessage, sessionId);
		ChatMessage resChatMessage = modelEntityMapper.mapAiMessageToChatMessage(resMessage, sessionId);
		
		reqChatMessage = messageRepository.save(reqChatMessage);
		log.info("Saved current User Input AI chat message, sessionId: {}, recordId: {}", reqChatMessage.getSessionId(), reqChatMessage.getId());
		resChatMessage = messageRepository.save(resChatMessage);
		log.info("Saved current Model Response AI chat message, sessionId: {}, recordId: {}", reqChatMessage.getSessionId(), reqChatMessage.getId());
		
		log.info("Getting count of messages related to the sessionId: {}", sessionId);
		long count = messageRepository.countBySessionId(sessionId);
		long summaryCount = summaryReposity.countBySessionId(sessionId);
		log.debug("Chat message count: {}, Summary count: {}", count, summaryCount);
		if(count > MAX_LIMIT_FOR_RECENT_CHATS) {
			boolean isImportant = false;
			if(summaryCount == 0) {
				log.info("Summarizing the conversation");
				// summarize the conversation
				List<ChatMessage> allMessages = messageRepository.findBySessionIdOrderByCreatedAtAsc(sessionId);
				String summary = summarize(allMessages);
				ChatSummary chatSummaryEntity = modelEntityMapper.mapChatSummary(summary, sessionId);
				chatSummaryEntity = summaryReposity.save(chatSummaryEntity);
				log.info("Saved chat summary, sessionId: {}, summaryId: {}", sessionId, chatSummaryEntity.getId());
				// store important tokens describing the entire conversation in vector db
				isImportant = isImportant(reqMessage.getContent(), resMessage.getContent());
			} else if (summaryCount > 0) {
				// Summary already exists - use the same summary and store important tokens in vector db
				isImportant = isImportant(reqMessage.getContent(), resMessage.getContent());
			} else {
				// Invalid count
			}
			// If important conversation - store in vector db
			if(isImportant) {
				vectorMemoryStore.saveMemory(sessionId, reqMessage.getContent() + " " + resMessage.getContent());
			}
		}
	}
	
	/** 
	 * @param allMessages List<{@link ChatMessage}>
	 * 
	 * 
	 * */
	private String summarize(List<ChatMessage> allMessages) {
		AiApiRequest aiApiRequest = buildRequest(allMessages);
		log.info("Calling LLM model to summarize chats for sessionId: {}", allMessages.get(0).getSessionId());
		String response = aiApiCaller.postApiCall(aiApiRequest);
		return response;
	}
	
	/** 
	 * @param text String
	 * 
	 * */
	private boolean isImportant(String text) {
		String lower = text.toLowerCase();
		return lower.contains("decision") ||
		           lower.contains("architecture") ||
		           lower.contains("design") ||
		           lower.contains("approach") ||
		           lower.contains("strategy") ||
		           lower.contains("we will") ||
		           lower.contains("we should") ||
		           lower.contains("important") ||
		           lower.contains("remember") ||
		           lower.contains("note that");
	}
	
	private boolean isImportant(String userInput, String aiResponse) {
		String combined = userInput + " " + aiResponse;
		return combined.length() > 80 &&
		           (
		             combined.contains("decision") ||
		             combined.contains("architecture") ||
		             combined.contains("design") ||
		             combined.contains("will use") ||
		             combined.contains("chosen") ||
		             combined.contains("selected")
		           );
	}
	
}
