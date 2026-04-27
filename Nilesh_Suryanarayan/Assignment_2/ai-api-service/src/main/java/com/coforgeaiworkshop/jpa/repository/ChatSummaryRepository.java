package com.coforgeaiworkshop.jpa.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.coforgeaiworkshop.jpa.entity.ChatSummary;

public interface ChatSummaryRepository extends JpaRepository<ChatSummary, Long> {

	Optional<ChatSummary> findBySessionId(String sessionId);
	
	long countBySessionId(String sessionId);
	
}
