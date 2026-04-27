package com.coforgeaiworkshop.service;

import static com.coforgeaiworkshop.AiRole.ASSISTANT;
import static com.coforgeaiworkshop.AiRole.USER;
import static com.coforgeaiworkshop.Application.createSessionId;

import java.time.LocalDateTime;
import java.util.Objects;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import com.coforgeaiworkshop.dto.AiConverseDTO;
import com.coforgeaiworkshop.dto.AiResponseDTO;
import com.coforgeaiworkshop.model.AiApiRequest;
import com.coforgeaiworkshop.model.AiMessage;
import com.coforgeaiworkshop.session.SessionStore;
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
	private AiApiCaller aiApiCaller;
	@Autowired
	private SessionStore sessionStore;
	
	@Autowired
	private ContextBuilderService contextEngine;
	
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
			log.info("Preparing request body and headers for ai-api communication", ollamaApiUrl);
			AiApiRequest aiApiRequest = contextEngine.buildRequest(aiConverseDto, sessionId); // new AiApiRequest(GLM_5_CLOUD_MODEL, messages, true);
			AiMessage reqAiMessage = new AiMessage(USER, aiConverseDto.getMessage(), "", LocalDateTime.now());
			log.info("Attempting to hit the Ollama API at: {}", ollamaApiUrl);
			String response = aiApiCaller.postApiCall(aiApiRequest);
			AiMessage resAiMessage = new AiMessage(ASSISTANT, response, "", LocalDateTime.now());
			contextEngine.addMessage(sessionId, reqAiMessage, resAiMessage);
			AiResponseDTO aiResponse = new AiResponseDTO(response, sessionId);
			return aiResponse;
		} else throw new HttpClientErrorException(HttpStatus.BAD_REQUEST);
	}
	
}
