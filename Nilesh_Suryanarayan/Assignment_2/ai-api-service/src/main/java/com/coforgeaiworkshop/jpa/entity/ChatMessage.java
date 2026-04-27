package com.coforgeaiworkshop.jpa.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "CHAT_MESSAGE")
public class ChatMessage {

	@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
	
	private String sessionId;
    private String role;

    @Column(columnDefinition = "TEXT")
    private String content;

    private LocalDateTime createdAt;
}
