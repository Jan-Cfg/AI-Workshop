Create a new .NET 10 API/Microservice. The service will follow clean architecture principles and adhere to .NET coding standards.

# Requirements:

1. The name of the project should be KafkaConsumerService.
2. Service objective: Consume Kafka messages from Azure Event Hubs published by external third‑party systems.
3. Add environment‑specific Event Hub broker endpoints in appsettings.{Environment}.json.
4. Implement message workflow:
   - Consume Kafka message
   - Insert payload into SQL database
   - After successful persistence, manually commit Kafka offset

5. Configure Kafka consumer settings (via IOptions pattern):
   - socket.timeout.ms = 60000
   - request.timeout.ms = 60000
   - metadata.request.timeout.ms = 60000

6. Integrate Datadog for structured logging, exception logging, and observability.
7. Create XUnit-based Unit Test project covering consumer logic, DB operations, and offset management.
8. Develop Azure DevOps CI/CD YAML pipelines for build, test, and deployment.
9. Ensure clean architecture, modular design, .NET coding standards, and SOLID principles throughout implementation.

# Output Requirements:

The overall implementation must:

1. Follow .NET coding standards
2. Apply Clean Architecture and modular design
3. Adhere strictly to SOLID principles
4. Support maintainability, extensibility, and clear separation of concerns
