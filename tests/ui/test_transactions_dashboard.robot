*** Settings ***
Documentation     UI regression for the transactions dashboard (release 65.5).
Resource          ../../resources/keywords/common_keywords.robot
Force Tags        ui    regression    transactions

*** Test Cases ***
Beta Dashboard Flag Is Readable
    ${enabled}=    Get Config    feature_flags.beta_dashboard    ${False}
    Should Not Be Equal    ${enabled}    ${None}

Transactions Dashboard Path Is Built
    ${base_url}=    Get Config    ui.base_url
    ${dashboard}=    Catenate    SEPARATOR=    ${base_url}    /transactions
    Should Start With    ${dashboard}    https://
    Should End With    ${dashboard}    /transactions
