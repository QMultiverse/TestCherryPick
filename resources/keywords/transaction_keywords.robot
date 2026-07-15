*** Settings ***
Documentation     Transaction-focused keywords (release 65.5).
Library           ../../libraries/transaction_validator.py
Resource          common_keywords.robot

*** Keywords ***
Get Settled Transactions
    [Documentation]    Return only transactions whose status is settled.
    ${all}=    Load Transactions
    ${settled}=    Create List
    FOR    ${txn}    IN    @{all}
        IF    '${txn}[status]' == 'settled'
            Append To List    ${settled}    ${txn}
        END
    END
    RETURN    ${settled}

Assert Transaction Is Valid
    [Arguments]    ${transaction}
    ${result}=    Validate Transaction    ${transaction}
    Should Be True    ${result}
