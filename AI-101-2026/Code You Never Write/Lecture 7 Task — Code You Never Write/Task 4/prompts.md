# Goal

Find Duplicate Photos and List them.

# Input

All the photos present in the folder where script is run.

# Output

- Produce a one-page HTML report containing a reconciled set of books: you know exactly which amounts are missing or unaccounted for, and who you still need to follow up with.

# Rules

- Expected Total: $200

# Nick Names

| Payment Record Name | Actual Person |
| ------------------- | ------------- |
| Alice W.            | Alice         |
| Bobby               | Bob           |
| Charlie             | Charlie       |
| D. Lee              | David         |
| Emma                | Emma          |
| F. Miller           | Frank         |
| Grace               | Grace         |
| Izzy                | Isabella      |
| Unknown User (Jack) | Jack          |

# Before Execution

- Read the files.
- First Inspect the file and report the column namesbefore doing this analysis.
- If any row can't be parsed, flag it, skip it and list it at the end.

# Verification

Show me manual checks for the :

- Nick name for Emma
- Payment history of Emma

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

Total the payments and Find the gap and identify the unmatched amounts and people that need follow-up.
