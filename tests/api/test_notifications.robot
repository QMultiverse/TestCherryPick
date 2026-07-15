*** Settings ***
Documentation     Notification-routing tests (release 65.5, round 3).
Library           ../../libraries/config_reader.py    ${ENV}
Library           ../../libraries/notification_service.py
Resource          ../../resources/keywords/common_keywords.robot
Force Tags        api    regression    notifications

*** Test Cases ***
Email Channel Is Enabled In QA
    ${notifications}=    Get Config    notifications
    ${service}=    Create Notification Service    ${notifications}
    ${enabled}=    Is Channel Enabled    email
    Should Be True    ${enabled}    Email notifications should be on in QA

Subject Line Reports Failures
    ${subject}=    Format Subject    Smoke Suite    ${8}    ${2}
    Should Contain    ${subject}    FAILED
    Should Contain    ${subject}    2 failed

*** Keywords ***
Create Notification Service
    [Arguments]    ${notifications}
    ${wrapper}=    Create Dictionary    notifications=${notifications}
    ${service}=    Evaluate
    ...    __import__('notification_service').NotificationService(${wrapper})
    RETURN    ${service}
