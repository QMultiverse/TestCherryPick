*** Settings ***
Documentation     Regression for case-insensitive user lookup (release 65.5, round 5).
Library           ../../libraries/data_loader.py
Force Tags        api    regression    users

*** Test Cases ***
Lookup Is Case Insensitive
    ${user}=    Find User    STANDARD_USER
    Should Not Be Equal    ${user}    ${None}    Uppercase username should still match

Lookup Ignores Surrounding Whitespace
    ${user}=    Find User    ${SPACE}standard_user${SPACE}
    Should Not Be Equal    ${user}    ${None}    Padded username should still match

Unknown User Returns None Or Raises
    ${passed}=    Run Keyword And Return Status    Find User    no_such_user
    Log    Lookup of unknown user completed (status=${passed})
