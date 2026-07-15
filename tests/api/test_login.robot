*** Settings ***
Documentation     Authentication API smoke tests.
Resource          ../../resources/keywords/login_keywords.robot
Force Tags        api    smoke

*** Test Cases ***
Valid User Can Build Login Payload
    ${user}=    Get Test User    standard_user
    ${payload}=    Build Login Payload    ${user}[username]    Str0ngP@ss
    Should Be Equal    ${payload}[username]    standard_user

Login Endpoint Is Configured
    ${endpoint}=    Resolve API Endpoint    login
    Should Be Equal    ${endpoint}    /auth/login
