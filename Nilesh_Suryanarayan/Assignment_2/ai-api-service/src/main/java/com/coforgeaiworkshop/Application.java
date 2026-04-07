package com.coforgeaiworkshop;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.converter.json.Jackson2ObjectMapperBuilder;
import org.springframework.web.client.RestTemplate;

import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.extern.slf4j.Slf4j;

import static com.coforgeaiworkshop.AppConstants.SESSION_ID_PREFIX;

import java.time.LocalDateTime;
import java.util.concurrent.atomic.AtomicInteger;

@Slf4j
@SpringBootApplication
public class Application {
	
	private static final int MAX_SEQUENCE = 9999;

	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
		log.info("AI API Service started...");
		String sessionId = createSessionId();
		System.out.println("Session ID: " + sessionId);
	}
	
	/* ****************************** Spring Beans ****************************** */
	
	@Bean
	public RestTemplate getRestTemplate() {
		return new RestTemplate();
	}
	
	@Bean
	public ObjectMapper objectMapper() {
		ObjectMapper objectMapper = new ObjectMapper().findAndRegisterModules();
		return objectMapper;
	}
	
	
	/* ****************************** Static methods ****************************** */
	
	/** 
	 * Generates a unique, patterned session id
	 * <br>Format: ollama-codex-00125534225660100
	 * 
	 * */
	public static String createSessionId() {
		AtomicInteger sequence = new AtomicInteger(0);
		long timestamp = System.currentTimeMillis();
		long threadId = Thread.currentThread().getId();
		int currentSequence = sequence.getAndIncrement() % MAX_SEQUENCE;
		String genNum = String.format("%d%02d%02d", timestamp, threadId % 1000, Math.abs(currentSequence));
		return SESSION_ID_PREFIX.concat(genNum);
	}
	
}
