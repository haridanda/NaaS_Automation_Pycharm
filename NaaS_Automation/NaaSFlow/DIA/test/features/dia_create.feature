Feature: Place DIA Order

  Scenario: Create DIA order
     Given login AutoPilot
     When validate Port avalibility
     Then create UNI
     And get uni info