# Optimized Prompt: Update Tennis Court Check Workflow with UV

## Objective
Update the `tennis_court_check` workflow to utilize `uv` for fast dependency installation, ensuring the environment is always up-to-date without sacrificing performance.

## Target File
`c:\Users\irubw\geminiProject\.agent\workflows\automation\tennis_court_check.md`

## Changes
1.  **Install Dependencies**: Add `uv pip install -r requirements.txt` before the execution step.
2.  **Context**: Ensure the commands are run within the correct directory (`c:\Users\irubw\geminiProject\tennis_reservation_checker`).
3.  **Optimization**: Leverage `uv`'s caching and speed.

## Implementation Steps
1.  Read the current content of `tennis_court_check.md`.
2.  Modify the "Setup & Execution" section to include the `uv` installation command.
3.  Verify the markdown syntax.
