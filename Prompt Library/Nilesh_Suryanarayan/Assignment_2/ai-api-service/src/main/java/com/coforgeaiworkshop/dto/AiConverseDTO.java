package com.coforgeaiworkshop.dto;

import org.springframework.stereotype.Component;
import org.springframework.validation.annotation.Validated;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
@Validated
@Component
public class AiConverseDTO {

	@NotNull
	private String message;
	@NotNull
	private String sessionId;
	
}
