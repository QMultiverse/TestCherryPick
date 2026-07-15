*** Settings ***
Documentation     Login-related keywords built on top of the common resource.
Resource          common_keywords.robot

*** Keywords ***
Build Login Payload
    [Arguments]    ${username}    ${password}
    ${payload}=    Create Dictionary    username=${username}    password=${password}
    RETURN    ${payload}

Login Should Be Rejected
    [Arguments]    ${status_code}
    Should Be Equal As Integers    ${status_code}    ${HTTP_UNAUTHORIZED}
    ...    Expected login to be rejected with 401
