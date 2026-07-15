*** Settings ***
Documentation     Structured-logging formatter tests (release 65.5, round 4).
Library           ../../libraries/log_formatter.py    logging-suite
Force Tags        api    regression    logging

*** Test Cases ***
Event Is Rendered As JSON
    ${line}=    Format Event    INFO    started    env=qa
    Should Contain    ${line}    "level":"INFO"
    Should Contain    ${line}    "message":"started"
    Should Contain    ${line}    "env":"qa"

Failed Result Is Error Level
    ${line}=    Format Result    Login Test    FAIL    1234
    Should Contain    ${line}    "level":"ERROR"
    Should Contain    ${line}    "status":"FAIL"

Unknown Level Is Rejected
    Run Keyword And Expect Error    *Unknown log level*    Format Event    TRACE    nope
