Project title and what it does.

## Which AI tool(s) and app(s) you used.

- Claude.ai
- Claude Code
- Google Drive Connector

## The prompts you used (and how you refined them).

I used a deatailed Prompt for it which is as follows:

## How you tested or verified that it worked.

I tested it via this prompt:

```
Use Google Drive Connector.
In the Agents Folder,
read the file INDU and create me a linkedin post for it
```

and refined it for every time it failed, this resulted in adding:

1. Explicitly identifying and stating Request Types in an organized manner.
2. Request Classification Table.
3. User Confimation as an explicit stage instead of just a table column.
4. Hard Constraints
5. Guard Clauses
6. Breaking down Workflow in Stages

## What worked, what did not, and any problems you faced.

Didnt work:

- Placing User Confirmaton as a requirement in the table
- Using Answering Model Haiku

What worked:

- Making an explicit Confirmaton stage.
- Breaking Workflow down in stages.

Problems Faced:

- Wrong Classification of my request
- Full Goole Drive Access not folder scoped
- Model skipping instruction execution

## For Task 1: why you chose your Skill and how it helps your daily life.

It helps me in building Linkedin Posts with the right strategy to market my skills.

## For Task 5: your safety assessment and verdict.

The skill i installed was assessed a safe as it didnt call any other external server and no asking for payment or password.
