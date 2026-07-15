*** Settings ***
Documentation     Accounts API smoke tests.
Resource          ../../resources/keywords/common_keywords.robot
Force Tags        api    regression

*** Test Cases ***
Standard User Has Accounts
    ${user}=    Get Test User    standard_user
    ${accounts}=    Accounts For Owner    ${user}[id]
    ${count}=    Get Length    ${accounts}
    Should Be True    ${count} >= 1    Expected at least one account for standard_user

Accounts Endpoint Is Configured
    ${endpoint}=    Resolve API Endpoint    accounts
    Should Be Equal    ${endpoint}    /accounts
