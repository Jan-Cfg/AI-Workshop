You are working on a Java Spring Boot application located in com.fatafat package. The project uses standard Spring‑style controllers, services, repositories, DTOs and entities, with JWT security and JPA repositories.

Task : Implement a new feature in the Delivery module that enables delivery partners to mark a delivery as completed. Upon saving this status, the system should also capture and store the partner’s current location and timestamp.

Requirements:

Follow the existing package structure and naming conventions (controller, service, repository, dto, entity, etc.).
Use Lombok or standard getters/setters as in the current codebase.
Add appropriate REST endpoints in a controller, service methods, and repository queries.
Validate inputs and return meaningful DTOs/responses.
Include unit tests for new classes/methods, following the style of existing tests (if any).
Update application.properties or other config if needed.
Ensure JWT security rules are applied as in SecurityConfig.
Keep formatting, logging, and error handling consistent with current code.
Add any necessary database migration or JPA annotations for new entities.
Document new API endpoints in README or documentation files.
Write Test case to have at least 90% coverage