---
name: project-retrospective
description: Create and maintain project retrospectives that record each meaningful interaction turn: the user's exact ask, Codex's interpretation, work performed, key findings, the user's response, and what Codex got right, wrong, or missed. Use when the user asks for retrospectives, interaction logs, after-action reviews, collaboration memory, turn-by-turn project records, or when updating an existing project retrospective log.
title: Project Retrospective
short_description: Create durable project retrospectives and interaction logs that preserve user asks, Codex interpretations, work performed, findings, responses, and lessons learned.
expanded_description: Use this skill when a user wants a project memory, after-action review, turn-by-turn interaction log, sprint retrospective, collaboration record, or durable project journal. It separates what the user asked from what Codex inferred, records work and findings, and captures what went right, wrong, or was missed.
aliases:
  - project memory
  - interaction log
  - after action review
  - collaboration memory
  - project journal
categories:
  - Documentation
  - Project Memory
  - Business Workflows
tags:
  - documentation
  - project-memory
  - retrospective
  - interaction-log
tasks:
  - create a project retrospective
  - update an interaction log
  - capture a project memory
  - write an after-action review
  - preserve decisions and lessons learned
use_when:
  - The user asks for a retrospective, interaction log, project memory, after-action review, or collaboration record.
  - The project needs a durable record of asks, interpretations, actions, findings, responses, and lessons.
do_not_use_when:
  - The user only wants a brief final summary and does not want a persistent project record.
  - The log would capture private or sensitive details that should not be written to the current repository.
inputs:
  - user request or project milestone
  - Codex interpretation and actions
  - key findings and validation results
  - user response when available
outputs:
  - retrospectives/interaction_log.md
  - optional interaction template
  - concise after-action review entries
examples:
  - Use project-retrospective to update this project's interaction log with what happened in this session.
  - Use project-retrospective to create an after-action review for this SkillForge milestone.
  - Use project-retrospective to capture what Codex got right, wrong, or missed in the last task.
related_skills:
  - get-youtube-media
risk_level: low
permissions:
  - local file read/write access to project retrospective files
page_title: Project Retrospective Skill - Project Memory, Interaction Logs, and After-Action Reviews for Codex
meta_description: Install the Project Retrospective Skill for Codex to preserve project memory, interaction logs, decisions, findings, and lessons learned.
---

# Project Retrospective

## What This Skill Does

Use this skill to create or update a durable retrospective record for project
work. The goal is to reduce expectation drift, preserve decisions, and make each
future turn smarter than the last one.

## Safe Default Behavior

Default to writing concise, factual project memory in the current workspace only
when the user wants a persistent record. Preserve the user's wording when
available, mark reconstructed entries clearly, and do not capture private or
sensitive details in repository files unless the user explicitly approves that
scope.

## Workflow

1. Locate the project retrospective file.
   - Prefer an existing `retrospectives/interaction_log.md`,
     `research-data/retrospectives/interaction_log.md`, or similarly named log.
   - If none exists and the user wants a persistent record, create a
     `retrospectives/` directory in the project with `interaction_log.md` and
     optionally `interaction_template.md`.
2. Add one entry per meaningful interaction or milestone.
   - Use the user's exact wording when available.
   - If reconstructing old turns, say that the entry is reconstructed.
   - Keep entries concise but candid.
3. Record the six required fields:
   - Exactly what the user asked.
   - What Codex thought the user asked.
   - Summary of what Codex did.
   - Key findings.
   - What the user's response was.
   - What Codex got right, wrong, or missed.
4. Make the interpretation gap explicit.
   - Name assumptions.
   - Name scope choices.
   - Note anything deferred or not verified.
5. Update the current turn's entry before finishing when possible.
   - If the user's response is not known yet, write `Pending after delivery`.
   - On the next turn, update that field if the response is now known.
6. If the project uses git, include retrospective changes in the next appropriate
   checkpoint unless the user asks not to.

## Entry Quality Rules

- Preserve the user's wording in a block quote when practical.
- Separate "what was asked" from "what was inferred"; do not blend them.
- Be specific about files, commits, searches, validations, and artifacts.
- Treat "wrong or missed" as useful engineering signal, not blame.
- Do not over-polish history. If something was uncertain, late, incomplete, or
  only partially verified, say so.
- Keep medical, legal, financial, or safety caveats attached to the relevant
  interaction when those domains are involved.

## Template

Use `references/interaction_entry_template.md` when creating a new log or when
the existing project has no preferred format.

## Reconstructed Entries

When creating retrospectives after the fact:

- Mark entries as reconstructed if exact details are incomplete.
- Prefer the actual user messages from the thread over memory.
- Use known commits, files, and command results to anchor the summary.
- Avoid inventing user reactions; write `Unknown`, `Pending`, or quote the next
  user message if it is clearly a response.

## Example

User asks: "make a retrospective for this sprint."

Good response behavior:

- Find or create the retrospective log.
- Add entries for the sprint's meaningful turns or milestones.
- Record asks, interpretations, actions, findings, user responses, and misses.
- Validate that the log is easy to continue next turn.
