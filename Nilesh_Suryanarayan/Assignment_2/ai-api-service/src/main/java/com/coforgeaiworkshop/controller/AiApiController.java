package com.coforgeaiworkshop.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.coforgeaiworkshop.dto.AiConverseDTO;
import com.coforgeaiworkshop.dto.AiResponseDTO;
import com.coforgeaiworkshop.service.AiApiService;

@RestController
public class AiApiController {
	
	@Autowired
	private AiApiService service;

	private static final String DESCRIPTION = "This is an API to communicate with a LLM model that \r\n"
			+ "			will answer your questions, chat with you and \r\n"
			+ "			provide solutions to your problems";
	
	@GetMapping("/")
	public ResponseEntity<String> describe() {
		return ResponseEntity.ok(DESCRIPTION);
	}
	
	@PostMapping("/ai-api-converse")
	public ResponseEntity<AiResponseDTO> aiApiConverse(@RequestBody AiConverseDTO requestDto) {
		AiResponseDTO aiResponse = service.callAiApi(requestDto);
		return ResponseEntity.ok(aiResponse);
	}
	
}
