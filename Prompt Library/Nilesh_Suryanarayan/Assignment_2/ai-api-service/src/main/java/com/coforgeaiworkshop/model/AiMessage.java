package com.coforgeaiworkshop.model;

import java.time.LocalDateTime;

import com.coforgeaiworkshop.AiRole;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AiMessage {

	private AiRole role;
	private String content;
	private LocalDateTime createUpdateTimestamp;
}
