# 🚀 Git & Bash Workflow Guide

This guide provides a comprehensive reference for navigating folders using Bash and managing Git repositories — from initialization to pushing code to GitHub, switching branches, and rolling back changes.

---

## 🧭 Bash Navigation Commands

| Command | Description |
|--------|-------------|
| `ls -d */` | Lists only folders (directories) in the current location. |
| `cd folder_name` | Changes into the specified folder. |
| `cd ..` | Moves up one directory level. |
| `ls` | Lists all files and folders in the current directory. |

---

## 🚀 Git Initialization & Remote Setup

| Command | Description |
|--------|-------------|
| `git init` | Initializes a new Git repository in the current folder. |
| `git remote add origin https://github.com/your-username/your-repo.git` | Links your local repo to a remote GitHub repository named `origin`. |

---

## 📦 Staging & Committing Changes

| Command | Description |
|--------|-------------|
| `git add .` | Stages all changes (new, modified, deleted files) in the current folder. |
| `git add filename` | Stages a specific file for commit. |
| `git commit -m "Your message"` | Commits staged changes with a descriptive message. |

---

## 🚀 Pushing to GitHub

| Command | Description |
|--------|-------------|
| `git push -u origin main` | Pushes your local `main` branch to the remote `origin` and sets it as the default upstream. |
| `git push` | Pushes committed changes to the remote branch (after upstream is set). |

---

## 🔀 Branch Management

| Command | Description |
|--------|-------------|
| `git branch` | Lists all local branches and shows the current one. |
| `git checkout branch-name` | Switches to an existing branch. |
| `git switch branch-name` | Newer syntax for switching branches. |
| `git checkout -b new-branch-name` | Creates and switches to a new branch. |
| `git switch -c new-branch-name` | Newer syntax for creating and switching to a new branch. |

---

## ⏪ Rollback & Undo

| Command | Description |
|--------|-------------|
| `git checkout -- filename` | Restores a file to its last committed state (undoes local changes). |
| `git reset filename` | Unstages a file (removes it from the staging area). |
| `git reset --soft HEAD~1` | Undoes the last commit but keeps changes staged. |
| `git reset --mixed HEAD~1` | Undoes the last commit and unstages changes. |
| `git reset --hard HEAD~1` | Undoes the last commit and discards all changes (dangerous). |
| `git revert commit-id` | Safely undoes a specific commit by creating a new one that reverses its changes. |

---

## 📁 Folder Structure & GitHub Behavior

- Git pushes the **contents** of the current folder, not the folder itself.
- If you want to push a folder as a subdirectory, go one level up and add the folder explicitly:
  ```bash
  cd ..
  git init
  git add Portfolio\&Documentation
  git commit -m "Add folder with contents"
  git remote add origin https://github.com/your-username/your-repo.git
  git push -u origin main