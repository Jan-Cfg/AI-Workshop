package com.coforgeaiworkshop.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AiResponseDTO {

	private String message;
	private String sessionId;
	
}
