package com.coforgeaiworkshop.jpa.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.coforgeaiworkshop.jpa.entity.ChatMessage;

public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {

	List<ChatMessage> findTop10BySessionIdOrderByCreatedAtDesc(String sessionId);

    long countBySessionId(String sessionId);

    List<ChatMessage> findBySessionIdOrderByCreatedAtAsc(String sessionId);
    
    List<ChatMessage> findBySessionIdOrderByCreatedAtDesc(String sessionId);
	
}
