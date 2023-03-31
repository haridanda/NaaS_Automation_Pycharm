from pytest_bdd import scenario, given, when, then

Feature: Place DIA Order

  Scenario: Create DIA order
     Given login AutoPilot
     When validate Port avalibility
     Then DIA Product E2E Validation

