---
name: handoff
description: Write a minimal, copy-ready prompt that lets a fresh chat continue the current work. Use when the user wants to move to a new chat, asks for a handoff or continuation prompt, or the context has grown long.
---

# Handoff prompt

Goal: the next chat continues immediately. At most four to five sentences, plain text in one code block, in the user's language.

Include only:

- where to start: working directory and "Lies AGENTS.md" (or the project's equivalent);
- the goal of the task in one sentence;
- the next steps in order, with exact paths;
- evidence instead of explanation: commits, files or specs that show how something was done;
- open decisions the user still has to make, and stop points such as "show the result and ask before committing".

Leave out what the next chat loads anyway (AGENTS.md, global instructions, skills, READMEs), history, reasoning and finished work unless it is the model to follow.

Durable versus temporary: knowledge every future project needs belongs in files (skill, README, AGENTS.md); propose that separately instead of putting it in the prompt. Knowledge needed only for this task stays in the prompt and is not written into files.

Before writing, check that referenced commits exist and paths are correct; name uncommitted work explicitly.
