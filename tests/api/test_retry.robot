*** Settings ***
Documentation     Retry-policy behaviour tests (release 65.5, round 2).
Library           ../../libraries/retry_policy.py    3    200
Force Tags        api    regression    retry

*** Test Cases ***
Retryable Status Triggers Another Attempt
    ${retry}=    Should Retry    ${503}    ${1}
    Should Be True    ${retry}    503 on attempt 1 should be retried

Non Retryable Status Stops
    ${retry}=    Should Retry    ${404}    ${1}
    Should Not Be True    ${retry}    404 must not be retried

Attempts Are Exhausted
    ${retry}=    Should Retry    ${503}    ${3}
    Should Not Be True    ${retry}    No retry once max attempts reached

Backoff Grows Exponentially
    ${first}=    Backoff Delay Ms    ${1}
    ${second}=    Backoff Delay Ms    ${2}
    Should Be True    ${second} > ${first}    Back-off must increase per attempt
