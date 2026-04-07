package com.coforgeaiworkshop.service;

import static com.coforgeaiworkshop.AppConstants.COMMA;
import static com.coforgeaiworkshop.AppConstants.GLM_5_CLOUD_MODEL;
import static com.coforgeaiworkshop.AppConstants.MAX_LIMIT_FOR_RECENT_CHATS;
import static com.coforgeaiworkshop.AppConstants.SYSTEM_PROMPT;
import static com.coforgeaiworkshop.Application.createSessionId;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import com.coforgeaiworkshop.AiRole;
import com.coforgeaiworkshop.dto.AiConverseDTO;
import com.coforgeaiworkshop.dto.AiResponseDTO;
import com.coforgeaiworkshop.model.AiApiRequest;
import com.coforgeaiworkshop.model.AiMessage;
import com.coforgeaiworkshop.session.SessionStore;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class AiApiService {
	
	@Autowired
	private RestTemplate restTemplate;
	@Autowired
	private ObjectMapper objectMapper;
	
	@Autowired
	private SessionStore sessionStore;
	
	@Value("${ai.api.url}")
	private String ollamaApiUrl;

	
	public AiResponseDTO callAiApi(AiConverseDTO aiConverseDto) {
		if (!Objects.isNull(aiConverseDto) && !StringUtils.isBlank(aiConverseDto.getMessage())) {
			// Generate session ID if not present
			String sessionId;
			if (StringUtils.isBlank(aiConverseDto.getSessionId())) {
				sessionId = createSessionId();
			} else {
				sessionId = aiConverseDto.getSessionId();
			}
			log.debug("Preparing request body and headers for ai-api communication", ollamaApiUrl);
			List<AiMessage> messages = getRecentHistory(sessionId, aiConverseDto.getMessage());
			
			AiApiRequest aiApiRequest = new AiApiRequest(GLM_5_CLOUD_MODEL, messages, true);
			HttpHeaders headers = new HttpHeaders();
			StringBuilder finalResponse = new StringBuilder();
			log.info("Attempting to hit the Ollama API at: {}", ollamaApiUrl);
			
			restTemplate.execute(
					ollamaApiUrl, 
					HttpMethod.POST, 
					request -> {
						headers.forEach((key, values) -> {
							request.getHeaders().set(key, String.join(COMMA, values));
							});
						objectMapper.writeValue(request.getBody(), aiApiRequest);
					}, 
					response -> {
	                    try (BufferedReader reader = new BufferedReader(
	                            new InputStreamReader(response.getBody(), StandardCharsets.UTF_8))) {

	                        String line;
	                        while ((line = reader.readLine()) != null) {
	                        	log.debug("token: {}", line);
	                            if (line.isBlank()) {
	                                continue;
	                            }

	                            JsonNode jsonNode = objectMapper.readTree(line);

	                            JsonNode messageNode = jsonNode.path("message");
	                            JsonNode thinkNode = messageNode.path("thinking");
	                            JsonNode contentNode = messageNode.path("content");
	                            System.out.print(thinkNode + " ");

	                            if (!contentNode.isMissingNode() && !contentNode.isNull()) {
	                                String chunk = contentNode.asText();
	                                finalResponse.append(chunk);
	                            }

	                            // Stop streaming when done=true
	                            boolean done = jsonNode.path("done").asBoolean(false);
	                            if (done) {
	                                log.info("Streaming completed.");
	                                break;
	                            }
	                        }
	                    }
	                    return null;
	                }
			);
			sessionStore.addMessage(sessionId, new AiMessage(AiRole.ASSISTANT, finalResponse.toString(), LocalDateTime.now()));
			
			AiResponseDTO response = new AiResponseDTO(finalResponse.toString(), sessionId);
			return response;
			
		} else throw new HttpClientErrorException(HttpStatus.BAD_REQUEST);
	}
	
	/** 
	 * @param sessionId 
	 * @param message 
	 * <br><br>
	 * @return List of AiMessage
	 * 
	 * */
	private List<AiMessage> setupChatSession(String sessionId, String message) {
		AiMessage latestMessage = new AiMessage(AiRole.USER, message, LocalDateTime.now());
		sessionStore.addMessage(sessionId, latestMessage);
		List<AiMessage> messages = new ArrayList<AiMessage>();
		// Set system message
		AiMessage systemMessage = new AiMessage(AiRole.SYSTEM, SYSTEM_PROMPT, LocalDateTime.now());
		messages.add(systemMessage);
		
		// Add session history
		List<AiMessage> history = sessionStore.getMessages(sessionId);
		messages.addAll(history);
		
		return messages;
	}
	
	/** 
	 * 
	 * 
	 * */
	private List<AiMessage> getRecentHistory(String sessionId, String message) {
		List<AiMessage> history = setupChatSession(sessionId, message);
		int start = Math.max(0, history.size() - MAX_LIMIT_FOR_RECENT_CHATS);
		
		List<AiMessage> recentHistory = history.subList(start, history.size());
		recentHistory.add(0, new AiMessage(AiRole.SYSTEM, SYSTEM_PROMPT, LocalDateTime.now()));
		return recentHistory;
	}
	
}
