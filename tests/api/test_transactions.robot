*** Settings ***
Documentation     Transactions API tests (release 65.5).
Library           ../../libraries/transaction_validator.py
Resource          ../../resources/keywords/common_keywords.robot
Force Tags        api    regression    transactions

*** Test Cases ***
All Fixture Transactions Are Valid
    ${transactions}=    Load Transactions
    ${checked}=    Validate All    ${transactions}
    Should Be True    ${checked} >= 3    Expected at least three transactions validated

Net Amount Is Computed Correctly
    ${transactions}=    Load Transactions
    ${net}=    Net Amount    ${transactions}
    Should Be True    ${net} != 0    Net amount should be non-zero for fixtures

Transactions Endpoint Is Configured
    ${endpoint}=    Resolve API Endpoint    transactions
    Should Be Equal    ${endpoint}    /transactions
