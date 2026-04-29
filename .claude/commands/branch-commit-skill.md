# Branch, Commit & Push

Create a new branch in a folder, stage all pending changes, commit with a message, and push.

## Usage
`/branch-commit <folder/branchname> "<commit message>"`

## Steps

1. Create and switch to the new branch:
   ```
   git checkout -b <folder/branchname>
   ```

2. Show `git status` and `git diff` so the user can see what will be committed.

3. Stage all modified tracked files (do NOT use `git add .` — stage only the files shown as modified in `git status`, excluding anything that looks like secrets or unintended files such as `.env`).

4. Commit with the provided message (no `Co-Authored-By` trailer):
   ```
   git commit -m "<commit message>"
   ```

5. Push and set upstream:
   ```
   git push -u origin <folder/branchname>
   ```

6. Report the branch name and commit hash when done.

## Notes
- If no folder is given, default to `fix/` as the prefix.
- If the branch already exists, switch to it instead of creating it.
- Never add `Co-Authored-By` lines to the commit message.
