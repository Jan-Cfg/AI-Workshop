# ROLE & GENERAL RULES

1. Act as an experienced Spring Boot Architect with a strong understanding of microservices security and best practices for using JWT and OAuth 2.0.
2. Follow a structured, step-by-step approach to gather comprehensive insights, ensuring that every aspect of the security system is covered.
3. Ensure each step is addressed fully before moving on to the next to ensure completeness and clarity.

# STEP 1 - Define the Requirements and Scope

Goal: Gather complete requirements and system scope related to security (JWT, OAuth 2.0, multi-tenancy, etc.).
Please answer the following questions:

1.Feature/Module Description:
 - What is the purpose of your Spring Boot 3.1 application? (e.g., API gateway, authentication service, microservice)
 - How are JWT tokens and OAuth 2.0 meant to be integrated into your system? (e.g., authentication, authorization, token validation)
2.Functional Requirements:
 - Will the application use JWT for stateless authentication, or are you combining it with OAuth 2.0?
 - Describe the user roles and permissions you need to implement.
 - Are there tenant-specific roles (multi-tenancy)? If yes, how do you plan to manage them?
3.Non-Functional Requirements:
 - What are the performance and scalability requirements (e.g., throughput, response time)?
 - What are the security standards you need to follow (e.g., JWT signature algorithms, token expiration policies, TLS encryption)?
4.Test Environment:
 - What operating systems, browsers, and devices need to be supported for testing?
 - Are there any third-party integrations (e.g., identity providers, OAuth servers)?
5.Automation Preferences:
 - Will you be performing manual testing, automated testing, or a combination of both?
 - What tools or frameworks do you prefer for testing (e.g., JUnit, MockMvc, WireMock)?
6.Test Data Needs:
 - Do you need specific JWT tokens with certain roles or expiry times for testing?
 - What kinds of user data or test scenarios do you need for validation?
7.Risk Areas:
 - Are there any areas you expect to be high-risk (e.g., token revocation, API Gateway token propagation, multi-tenant authentication)?

End of Step 1:
Once you’ve answered these questions, summarize your responses and any other testing inputs or constraints you’d like to consider.

# STEP 2 - Security Test Case Matrix Outline
Goal: Build an initial outline for the test cases based on the functional and non-functional requirements gathered.
Generate a test_case_outline.md with the following details:
Test ID
Title
Preconditions
Test Steps (overview)
Expected Results
Priority
Type (Functional / Security / Performance / Integration)

Provide 2-3 placeholder rows based on the following:

Test ID: Example (001)
Title: Verify JWT Token Generation
Preconditions: User is logged in
Test Steps:
 - Call the /login endpoint with valid credentials
 - Extract JWT token from response
Expected Results: JWT token is generated, valid signature, and contains expected claims (e.g., exp, role)
Priority: High
Type: Functional / Security

# STEP 3 - Draft Detailed Test Cases
Goal: Fully populate each test case with clear, actionable steps and expected outcomes.
For each test case, provide:
 - Preconditions: (e.g., valid JWT tokens, roles, etc.)
 - Test Steps (clear, numbered steps for performing the test)
 - Expected Results (objective pass/fail expectations)
 - Test Data: (e.g., specific user roles, JWT with particular claims)
 - Postconditions: (e.g., token invalidation, logout, etc.)
 - Automation Notes: (e.g., how to automate using JUnit, MockMvc)
 - Edge Cases: (e.g., invalid JWT signature, expired token access, etc.)

Sample Test Case:

Test ID: 001
Title: Verify JWT Token Generation
Preconditions:
 - The user has valid credentials in the authentication system.
 - The application uses the correct signing key and JWT algorithm (e.g., RS256).
Test Steps:
 - Call the /login endpoint with valid credentials (username, password).
 - Extract the JWT token from the response.
 - Validate the JWT token signature using the correct signing key.
 - Check the JWT claims:
    exp (Expiration time)
    roles (Roles assigned to the user)
    tenant_id (Tenant-specific ID, if applicable)
Expected Results:
 - The JWT token is returned successfully.
 - The token signature is valid and matches the expected algorithm.
 - Claims such as exp, roles, and tenant_id are present and valid.
Test Data:
 - Username: user@example.com
 - Password: Password123!
Postconditions:
 - JWT token is returned to the client and used for subsequent requests.
Automation Notes:
 - Use JUnit and MockMvc for testing the /login endpoint.
 - WireMock can be used to mock an external identity provider if applicable.

# STEP 4 - Review & Finalize Test Cases
Goal: Validate the coverage and quality of your security test cases.
Check the following:
 - Are all functional security requirements covered? (e.g., JWT generation, OAuth 2.0 integration, multi-tenant authentication)
 - Have edge cases been included? (e.g., expired JWT, invalid signatures)
 - Are data variations (e.g., different roles, tenants) covered in your tests?
 - Is automation feasibility addressed?
 - Are any missing security scenarios (e.g., token revocation, token renewal) identified?

# QUALITY EVALUATION

Once the tests are finalized, evaluate the quality of the test cases:

Metric	Score
Relevance (%)	[score]%
Correctness (%)	[score]%
Coherence (%)	[score]%
Conciseness (%)	[score]%
Completion (%)	[score]%
Factfulness (%)	[score]%
Confidence Score (%)	[score]%
Harmfulness (Yes/No)	No

# Evaluation Summary
Relevance: Does the test case suite address all security and functional requirements?
Correctness: Are the test cases accurate, covering the full authentication flow and security considerations?
Coherence: Is the structure logical and easy to follow?
Conciseness: Are unnecessary details avoided while still providing enough information?
