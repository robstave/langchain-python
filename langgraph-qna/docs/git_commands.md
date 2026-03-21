# Git Commands Reference

## Setup and Configuration

### Initial Setup

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

### Useful Config Options

```bash
git config --global core.editor "code --wait"   # VS Code as editor
git config --global pull.rebase true             # rebase on pull
git config --global fetch.prune true             # auto-prune on fetch
git config --list                                 # show all config
```

## Creating Repositories

```bash
git init                    # initialize a new repo in current directory
git clone <url>             # clone a remote repository
git clone <url> <dirname>   # clone into a specific directory name
```

## Daily Workflow

### Staging and Committing

```bash
git status                  # show working tree status
git add <file>              # stage specific file
git add .                   # stage all changes
git add -p                  # interactively stage hunks
git commit -m "message"     # commit with message
git commit --amend          # modify the last commit
```

### Viewing Changes

```bash
git diff                    # unstaged changes
git diff --staged           # staged changes (about to commit)
git diff HEAD~3             # changes in last 3 commits
git log --oneline -10       # last 10 commits, compact format
git log --graph --oneline   # visual branch history
git show <commit>           # show a specific commit's changes
```

## Branching

### Creating and Switching

```bash
git branch                  # list local branches
git branch -a               # list all branches (including remote)
git branch <name>           # create a new branch
git checkout <name>         # switch to a branch
git checkout -b <name>      # create and switch in one step
git switch <name>           # modern way to switch branches
git switch -c <name>        # modern way to create and switch
```

### Merging

```bash
git merge <branch>          # merge branch into current
git merge --no-ff <branch>  # force a merge commit (no fast-forward)
git merge --abort           # abort an in-progress merge
```

When a merge conflict occurs, Git marks the conflicting sections in the files.
Edit the files to resolve conflicts, then `git add` and `git commit`.

### Rebasing

```bash
git rebase <branch>         # rebase current onto branch
git rebase -i HEAD~3        # interactive rebase last 3 commits
git rebase --abort          # abort an in-progress rebase
git rebase --continue       # continue after resolving conflicts
```

Rebase rewrites history by replaying commits on top of another branch. Never rebase
commits that have been pushed to a shared branch.

## Remote Operations

```bash
git remote -v                       # list remotes with URLs
git remote add <name> <url>         # add a new remote
git fetch                           # download remote changes (no merge)
git pull                            # fetch + merge (or rebase if configured)
git push                            # push current branch to remote
git push -u origin <branch>         # push and set upstream tracking
git push --force-with-lease         # force push safely (checks remote)
```

### Pull vs Fetch

- `git fetch` downloads remote changes but does NOT modify your working tree.
  It updates remote-tracking branches (e.g., `origin/main`).
- `git pull` is essentially `git fetch` + `git merge` (or `git rebase` if configured).
  It modifies your working tree.

Use `git fetch` when you want to see what's changed without affecting your work.

## Undoing Changes

```bash
git restore <file>          # discard working tree changes (modern)
git restore --staged <file> # unstage a file (modern)
git checkout -- <file>      # discard changes (older syntax)
git reset HEAD <file>       # unstage a file (older syntax)
git reset --soft HEAD~1     # undo last commit, keep changes staged
git reset --mixed HEAD~1    # undo last commit, keep changes unstaged
git reset --hard HEAD~1     # undo last commit, DISCARD all changes
git revert <commit>         # create a new commit that undoes a commit
```

### Reset vs Revert

- `git reset` rewrites history. Use only on local, unpushed commits.
- `git revert` creates a new commit undoing changes. Safe for shared branches.

## Stashing

```bash
git stash                   # stash working changes
git stash push -m "message" # stash with a description
git stash list              # list all stashes
git stash pop               # apply most recent stash and remove it
git stash apply             # apply most recent stash but keep it
git stash drop              # delete most recent stash
git stash clear             # delete all stashes
```

Stash is useful when you need to switch branches but have uncommitted work.

## Tags

```bash
git tag v1.0.0              # lightweight tag
git tag -a v1.0.0 -m "msg" # annotated tag (recommended for releases)
git push origin v1.0.0      # push a specific tag
git push origin --tags       # push all tags
```

## Useful Debugging

```bash
git blame <file>            # show who last modified each line
git bisect start            # begin binary search for a bug
git bisect bad              # mark current commit as bad
git bisect good <commit>    # mark a known-good commit
git bisect reset            # end bisect session
```

`git bisect` performs a binary search through commit history to find which commit
introduced a bug. It's extremely efficient for large histories.
