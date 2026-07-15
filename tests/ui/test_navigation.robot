*** Settings ***
Documentation     UI navigation smoke tests (placeholder assertions).
Resource          ../../resources/keywords/common_keywords.robot
Force Tags        ui    smoke

*** Test Cases ***
UI Base URL Is Configured
    ${base_url}=    Get Config    ui.base_url
    Should Start With    ${base_url}    https://

Default Browser Is Set
    ${browser}=    Get Config    ui.browser
    Should Not Be Empty    ${browser}
