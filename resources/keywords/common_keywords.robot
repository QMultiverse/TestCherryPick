*** Settings ***
Documentation     Reusable keywords shared across API and UI suites.
Library           ../../libraries/config_reader.py    ${ENV}
Library           ../../libraries/data_loader.py
Variables         ../variables/global_variables.py

*** Keywords ***
Resolve API Base URL
    [Documentation]    Return the API base URL for the active environment.
    ${base_url}=    Get Config    api.base_url
    RETURN    ${base_url}

Resolve API Endpoint
    [Arguments]    ${name}
    ${path}=    Get Config    api.endpoints.${name}
    RETURN    ${path}

Get Test User
    [Arguments]    ${username}
    ${user}=    Find User    ${username}
    Should Not Be Equal    ${user}    ${None}    User '${username}' not found in test data
    RETURN    ${user}
