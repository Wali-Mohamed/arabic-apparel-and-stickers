# AI Agent Workflow

## Purpose

This document distinguishes the project's documented Codex-assisted work from a
proposed multi-agent workflow. It does not claim that proposed agents have run.

## Documented current use of OpenAI Codex

OpenAI Codex was used interactively with human direction to inspect the
repository, implement product and reproducibility changes, run Docker Compose,
run backend and frontend tests, investigate migration failures, review diffs,
and create commits when explicitly requested. The commit history is supporting
repository evidence for iterative changes; it does not identify which tool or
person authored each commit.

The current documented workflow is human-in-the-loop:

1. The product owner supplies a scoped request and constraints.
2. Codex inspects relevant code and documentation before editing.
3. Codex implements bounded changes and reports commands and results.
4. The product owner reviews outcomes and explicitly authorizes irreversible
   actions such as commits and pushes.

This repository has no evidence of an executed autonomous agent team, custom
agent loop or project-specific MCP server. The
roles below are proposed operating instructions, not historical execution logs.

## Proposed agent team

| Role | Scope | May do | Must not do |
| --- | --- | --- | --- |
| Planner | Turn product requests into small tasks and acceptance criteria | Read docs/code, update the Markdown tracker | Edit application code, run destructive commands, claim tests passed |
| Implementer | Make one approved task's code and documentation changes | Edit scoped files, run targeted tests | Commit/push, reset data, approve its own work |
| Reviewer and tester | Independently assess diff and run checks | Read-only review, run tests/builds, record findings | Modify implementation while reviewing, mark known failures as passed |
| Operations | Reproduce Compose startup, migrations, and endpoint checks | Use isolated project names/temporary volumes, inspect logs | Touch existing volumes, reset databases, deploy, or force-push |

## Collaboration protocol

1. The planner creates or refines one tracker item with scope, acceptance
   criteria, risks, and verification commands.
2. The implementer reads `AGENTS.md`, `spec.md`, architecture, and the assigned
   tracker item; it records changed files and tests in that item.
3. The reviewer/tester reads the implementation diff and independently runs the
   stated checks. Failures return the item to implementation with evidence.
4. The operations role uses a distinct Docker Compose project name and fresh
   volume for reproducibility checks. It never deletes the developer's existing
   database volume.
5. A human reviews the evidence and decides whether to commit, push, or release.

For parallel work, agents use separate Git worktrees and own non-overlapping
files. They exchange only concise tracker handoffs: task ID, decision, changed
files, commands, results, blockers, and next owner.

## Context-management rules

- `AGENTS.md` is the durable entry point; do not duplicate the full architecture
  or product specification in prompts.
- Use `docs/TASK_TRACKER.md` as the local source of task status and evidence.
- Read only the files relevant to the assigned task, then summarize findings in
  the tracker rather than relying on long chat history.
- Preserve hard constraints in the task handoff: no secrets, no unapproved
  commits/pushes, and no destructive database actions.

## Rubric gap

The [public GitHub Issues tracker](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues)
was created on 2026-10-26 from the specification, local tracker and agent
instructions, checked against the current official rubric. Issues include
acceptance criteria, priorities and evidence requirements. The local tracker
records this agent-assisted backlog creation and the
[actual Issue #1 review](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/1#issuecomment-6421542642).
The review was performed by the same agent as the implementer and does not
satisfy independent validation. Issue #1 remains open for independent review.
Proposed multi-agent roles above remain proposals.
