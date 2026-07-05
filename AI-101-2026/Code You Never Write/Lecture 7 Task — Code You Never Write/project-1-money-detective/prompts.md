# Goal

Uncover Spending Patterns, Forgotten Subscriptions, and Duplicate Charges

# Input

Attached is a PDF file 'AccountStatement.pdf' that contains my spending history with rows containing :

- Date Transaction
- Type Channel Transaction
- Description
- Money In
- Money Out
- Fee Balance

# Output

- Produce a one-page HTML report containing:
  1. Spending Patterns
  2. Forgotten Subscriptions
  3. Duplicate Charges
  4. monthly trend chart
  5. category table
  6. duplicates list
  7. three observations worth my attention.

# Rules

- Spending after midnight are leaks.
- Do not estimate, Compute the result from the data.

# Edge Cases

- Amounts above 30,000 Rs are not to be analyzed.
- Exclude NADRA Billing Transactions

# Before Execution

- Read the AccountStatement pdf file.
- First Inspect the file and report the row count, column names, and date range before doing this analysis.
- If any row can't be parsed, skip it and list it at the end.

# Verification

Show me manual checks for:

- Total Donations made till date
- Biggest Transaction amount in the spending with date and time
- Smallest Transaction amount in the spending with date and time

# Execution Guidelines

- Never Simulate the process
- If you cant Run the Code, explicity report at the start.
- Never estimate or make guess.
- Write and Run Code to answer this.
- Show me the code you run.

# Script Specifications

- The Script should not contain the parsed data.
- The Script should contain the logic to be able to import , parse and perform computations on the data.
- Run the Script to get the results.
- The Script should be reusable and runnable from the commandline.

# Script Execution Report

Answer the following questions:

1. Do you have access to a working execution environment for the script ?
2. Did you run the prepared script at last with no errors found ?
3. Explain me the logic you wrote in the script.

Write a script for this brief and run it.
