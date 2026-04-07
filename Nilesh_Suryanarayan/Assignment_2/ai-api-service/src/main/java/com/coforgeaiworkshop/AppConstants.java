package com.coforgeaiworkshop;

public interface AppConstants {

	public static final String SYSTEM_PROMPT = """
			You are a helpful AI assistant specialized in software engineering, Java, Spring Boot, and microservices.
			Be concise, practical, and technically accurate when explaining concepts, use step-by-step examples
			""";
	
	public static final String AI_USER_ROLE = "user";
	public static final String GLM_5_CLOUD_MODEL = "glm-5:cloud";
	public static final String SESSION_ID_PREFIX = "ollama-codex-";
	public static final int MAX_LIMIT_FOR_RECENT_CHATS = 10;
	
	public static final String COMMA = ",";
}
