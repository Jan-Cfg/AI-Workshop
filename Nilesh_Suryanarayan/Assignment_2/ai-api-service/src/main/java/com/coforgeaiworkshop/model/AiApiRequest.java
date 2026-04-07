package com.coforgeaiworkshop.model;

import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder.Default;
import lombok.Data;

@Data
@AllArgsConstructor
public class AiApiRequest {

	private String model;
	private List<AiMessage> messages;
	private boolean stream = true;
	
}
