# Goal

Find Duplicate Photos and List them.

# Input

All the photos present in the folder where script is run.

# Output

- Produce a script that detects all the photos in the folder, finds their duplicates and lists the deletion plan.
- Two outputs are needed:

1. Plan
2. Associated Script

# Rules

- Dont delete or update anything, but test the script in your runtime.
- Plan is supposed to be a step by step solution which solves the problem with the script.
- The script needs to create a backup for the folder it will operate on first.

# Checkpoints

- It should be done in checkpoints
- The first checkpoint analyzes the folder and outputs the plan in the html in 'plan.html' and outputs the commandline.
- After showing the plan on the commandline, it asks the user to proceed with the backup or not.
- If the user permits it on the commandline, it creates the backup successfully and notifies the user in the commandline. This is the second checkpoint. The commandline asks user to check if the backup is created.
- The backup process should not copy the 'plan.html' and any file which is associated with running of duplication removal process.
- Now the commandline shows the user the next phase of the execution where it is about to delete the files and list the relevant details
- Asks the user to proceed with the final operation of removing duplication
- Receives user's answer.
- If yes then remove the output and produce the final report of execution in the commandline and in html.
- If no then skip the deletion and produce the final report of execution in the commandline and in html.

# Before Execution

- Read only photos the files.
- If any row can't be parsed, flag it, skip it and list it at the end.

# Verification

Show me manual checks for the :

- how many images do you see in the folder
- tell me the last image in the folder

# Execution Guidelines

- Never Simulate the process
- If you cant Run the Code, explicity report at the start.
- Never estimate or make guess.
- Write and Run Code to answer this.
- Show me the code you run.

# Script Specifications

- Run the Script to get the results.
- The Script should be reusable and runnable from the commandline.

# Script Execution Report

Answer the following questions:

1. Do you have access to a working execution environment for the script ?
2. Did you run the prepared script at last with no errors found ?
3. Explain me the logic you wrote in the script.
