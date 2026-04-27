package com.coforgeaiworkshop.service;

import static com.coforgeaiworkshop.AppConstants.COMMA;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.coforgeaiworkshop.model.AiApiRequest;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class AiApiCaller {

	@Autowired
	private RestTemplate restTemplate;
	@Autowired
	private ObjectMapper objectMapper;
	
	@Value("${ai.api.url}")
	private String ollamaApiUrl;
	
	public String postApiCall(AiApiRequest aiApiRequest) {
		HttpHeaders headers = new HttpHeaders();
		StringBuilder finalResponse = new StringBuilder();
		
		restTemplate.execute(
				ollamaApiUrl, 
				HttpMethod.POST, 
				request -> {
					headers.forEach((key, values) -> {
						request.getHeaders().set(key, String.join(COMMA, values));
						});
					objectMapper.writeValue(request.getBody(), aiApiRequest);
				}, 
				response -> {
                    try (BufferedReader reader = new BufferedReader(
                            new InputStreamReader(response.getBody(), StandardCharsets.UTF_8))) {

                        String line;
                        while ((line = reader.readLine()) != null) {
                        	log.debug("token: {}", line);
                            if (line.isBlank()) {
                                continue;
                            }

                            JsonNode jsonNode = objectMapper.readTree(line);

                            JsonNode messageNode = jsonNode.path("message");
                            JsonNode thinkNode = messageNode.path("thinking");
                            JsonNode contentNode = messageNode.path("content");
                            System.out.print(thinkNode + " ");

                            if (!contentNode.isMissingNode() && !contentNode.isNull()) {
                                String chunk = contentNode.asText();
                                finalResponse.append(chunk);
                            }

                            // Stop streaming when done=true
                            boolean done = jsonNode.path("done").asBoolean(false);
                            if (done) {
                                log.info("Streaming completed.");
                                break;
                            }
                        }
                    }
                    return null;
                }
		);
		
		return finalResponse.toString();
	}
	
}
