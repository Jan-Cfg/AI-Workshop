package com.coforgeaiworkshop;

public enum AiRole {
	
	SYSTEM("system"),
	USER("user"),
	ASSISTANT("assistant");
	
	private final String role;
	
	AiRole(String role) {
		this.role = role;
	}
	
	public String getRole() {
		return this.role;
	}
}
