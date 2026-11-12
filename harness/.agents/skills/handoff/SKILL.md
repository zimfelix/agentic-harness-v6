---
name: handoff
description: Write a compact but loss-free, copy-ready prompt that lets a fresh chat continue the current work. Use when the user wants to move to a new chat, asks for a handoff or continuation prompt, or the context has grown long.
---

# Handoff prompt

Goal: a fresh chat with only this prompt plus the repository continues without asking what was meant and without reopening settled questions. Compact, but nothing from the chat that matters may be lost. Starting fresh with a good handoff beats a bloated context; the prompt carries what exists only in this chat, the repo carries the rest.

## 1. Collect before writing

Go through the whole conversation, not just the last messages, and note what exists **only in the chat** and not in any file:

- decisions and their one-line reason, so they are not reopened;
- corrections and preferences the user stated (wording, scope, "not X", tone), in their words where wording matters;
- dead ends: what was tried and failed, and why;
- current state: done, half done, uncommitted, running or published, with exact paths, commits, URLs;
- open questions and decisions the user still has to make;
- constraints and stop points ("show before committing", "do not touch file Y").

Check that referenced commits exist and paths are correct (`git status`, `git log`).

## 2. Write the prompt

Plain text in one code block, in the user's language, short headed lines or bullets, one fact per line:

- **Start:** working directory, "Lies AGENTS.md" (or the project's equivalent) and any file the next step depends on.
- **Ziel:** the task in one sentence.
- **Stand:** what is done (by evidence: commit, file, URL), what is not.
- **Entscheidungen / Vorgaben:** items from step 1, one line each with reason.
- **Sackgassen:** only if any.
- **Nächste Schritte:** in order, with exact paths and commands.
- **Offen / Stopp:** decisions for the user and stop points.

Leave out what the next chat loads or can read anyway (AGENTS.md content, global instructions, skills, READMEs, code), history and narration. Point to files instead of copying them. Length follows the content: usually 10–30 lines; a short task can be three lines. Never drop a chat-only decision to save space; shorten its wording instead.

Durable versus temporary: knowledge every future chat or project needs belongs in files (learning state, AGENTS.md, skill); propose that separately, do not write it silently. Task-only knowledge stays in the prompt.

## 3. Check and deliver

Cold-start test before output: "Could a new agent act correctly with only this prompt and the repo? Would it repeat a dead end or ask the user something already settled?" Fix gaps.

Copy the prompt to the clipboard with exactly the code-block text (macOS: `cat <<'EOF' | pbcopy`). Say in one line that it has been copied, or that copying failed. Below the block, name in one line anything deliberately left out or proposed for a durable file.
