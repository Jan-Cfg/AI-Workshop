#### AI API micro-service

###### Description:
Spring-boot service acting as a context engine for the Ollama based Codex LLM model running in the local environment

The service exposes a POST endpoint `/ai-api-converse` that takes below request body. The message is the user input and the sessionId is maintained per session. If it is a first request then the sessionId is created and stored in the session store. The user input is passed to the Ollama's chat API endpoint `/api/chat`. And it's response is again stored in the session store with the role as **assistant**. And from the spring-boot endpoint a response is returned along with the sessionId. So while processing the consecutive requests, this sessionId is used to extract past conversations - which are all sent to the AI API to get better results. 
###### Request
```
{
  "message": "Enter user innput",
  "sessionId": ""
}
```
###### Response
```
{
  "message": "LLM response",
  "sessionId": "ollama-codex-00125534225660100"
}
```

###### Recent history
>
A concept of Recent history has been implemented, simply passing past 10 conversation messages only to the AI API to reduce the overload of messages and slow down the performance.
>

###### Summarization
*Summarization is yet to be implemented.* The idea is if the number of messages increase a certain limit, then we'll ask the AI to summarize those messages while keeping the user preferences, technical decisions and other constraints intact. **Summary** will be stored separately along with the list of messages in the session store. So now we'll send these below items to the LLM model which will give us proper response.
1. System Prompt
2. Conversation summary
3. Recent history (Last n messages)
4. Lastest user input


###### Vector database implementation
