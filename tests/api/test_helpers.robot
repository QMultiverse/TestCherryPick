*** Settings ***
Documentation     Tests for the consolidated helpers module (release 65.5, round 6).
Library           ../../libraries/helpers.py
Force Tags        api    regression    helpers

*** Test Cases ***
Deep Get Reads Nested Values
    ${data}=    Evaluate    {'a': {'b': {'c': 42}}}
    ${value}=    Deep Get    ${data}    a.b.c
    Should Be Equal As Integers    ${value}    42

Mask Secret Reveals Last Two Characters
    ${masked}=    Mask Secret    supersecret
    Should End With    ${masked}    et
    Should Start With    ${masked}    *

Mask Secret Rejects Non String
    Run Keyword And Expect Error    *expects a string*    Mask Secret    ${12345}
