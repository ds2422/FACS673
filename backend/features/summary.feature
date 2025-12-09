Feature: Nexus AI Summarization Flow

  Scenario: User logs in and summarizes text
    Given I open the Nexus AI application
    And I enter "test@example.com" into the email field
    And I enter "password123" into the password field
    And I click the Login button
    Then I should see the dashboard

    When I enter "Artificial Intelligence is rapidly evolving." into the first text input
    And I click the Synthesize button
    Then I should see the Summary Result section
    And the summary should contain text