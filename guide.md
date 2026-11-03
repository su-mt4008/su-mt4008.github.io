---
outline: [2, 3]
---

# How we work

In this course you work the way data scientists work in industry and research. Every assignment
and the project live in a **Git repository on GitHub**. You hand in by opening a **pull request**,
classmates and teachers review it like code is reviewed at work, and an **automatic check**
proves that your report runs on someone else’s computer.

This page is the reference for all of it. Set up once (about an hour), then follow
[Hand in an assignment](#hand-in-an-assignment) every week.

## The tools

| Tool | What it does |
|---|---|
| **VS Code** | The one program you work in: editor, terminal, Git and pull requests. |
| **Git** | Records every version of your work. |
| **GitHub** | Hosts your repository; where you hand in and review. |
| **Quarto** | Turns `report.qmd` (text + code) into `report.md`, a report with results and figures. |
| **uv** (Python) or **renv** (R) | Installs exactly the package versions listed in your project, on any computer. |

You choose **Python or R** at the start and use it for the whole course.

## Set up your computer {#set-up-your-computer}

Do these in order. If something fails, ask in a session, or use
[the fallback](#if-your-install-fails) for now.

### 1. GitHub account

Create an account at <https://github.com> if you don’t have one, and register your username on
<a :href="$course.links.moodle">Moodle</a>. We use it to create your repositories in the
`su-mt4008` organisation. Accept the invitation email from GitHub when it arrives.

### 2. VS Code and its extensions

1. Install VS Code from <https://code.visualstudio.com>.
2. Open the **Extensions** view (the four-squares icon on the left, or `Ctrl+Shift+X`;
   `Cmd+Shift+X` on a Mac) and install:
   - **Quarto** (by Quarto)
   - **GitHub Pull Requests** (by GitHub)
   - Python users: **Python** and **Jupyter** (by Microsoft)
   - R users: **R** (by REditorSupport)
3. Sign in to GitHub: click the **Accounts** icon (bottom left) → **Sign in with GitHub**.

R users can also use **Positron** (<https://positron.posit.co>), Posit’s editor built on VS Code.
Everything on this page works the same there.

<!-- TODO(owner): screenshot of the Extensions view with the extensions installed. -->

### 3. Git

- **Mac:** open the Terminal and run `git --version`. If Git is missing, macOS offers to install it; accept.
- **Windows:** install Git for Windows from <https://gitforwindows.org>. Keep the defaults, but choose
  **VS Code** as Git’s default editor when asked.

Then tell Git who you are (once, in VS Code’s terminal: **Terminal → New Terminal**):

```bash
git config --global user.name "Your Name"
git config --global user.email "the-email-on-your-github-account@example.com"
```

### 4. Quarto

Install Quarto from <https://quarto.org/docs/get-started/>. Check it in the terminal:

```bash
quarto --version
```

### 5. Your language

:::code-group
```bash [Python (Mac/Linux)]
# uv installs Python for you; you don't need to install Python separately.
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```
```powershell [Python (Windows)]
# In PowerShell (VS Code's default terminal on Windows):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```
```r [R]
# 1. Install the current R (4.6 or newer) from https://cloud.r-project.org
#    (Windows: "base"; Mac: the .pkg for your chip).
# 2. Then, in the R console:
install.packages("renv")
```
:::

Close and reopen VS Code after installing, so it finds the new programs.

## Hand in an assignment {#hand-in-an-assignment}

Every assignment works the same way. Example for HW1; use your own username and the right number.

### 1. Clone your repository

We create a private repository for you for each assignment, named `<username>-hw1`, from the
course template. In VS Code: **Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`) →
**Git: Clone** → **Clone from GitHub** → choose `su-mt4008/<username>-hw1` → pick a folder → **Open**.

### 2. Install the project’s packages

In VS Code’s terminal, inside the repository:

:::code-group
```bash [Python]
uv sync
```
```r [R]
# In an R console started in the repository folder (see below):
renv::restore()
```
:::

This installs exactly the versions in `uv.lock` / `renv.lock`, the same as on every other
computer, including the check. Do it again whenever the lockfile changes.

**R users:** R must start *in the repository folder*, or `renv` won’t find your project. In VS
Code, open the repository folder, then **Command Palette** → **R: Create R Terminal**: it starts
in the folder you have open. (In Positron, the Console already does.) Don’t use R.app or RGui
for this; they start in your home folder.

### 3. Make a branch

Click the branch name **main** in the bottom-left corner → **Create new branch…** → type `hw1` →
Enter. You now work on `hw1`; `main` stays as it was.

### 4. Do the work

Write your analysis in `report.qmd`, section by section. Render it often:

:::code-group
```bash [Python]
uv run quarto render report.qmd
```
```bash [R]
quarto render report.qmd
```
:::

Open `report.md` to see the result. That file, with its figures in `report_files/`, is what your
reviewers read on GitHub, so commit it too.

Need another package? Python: `uv add seaborn`. R: `install.packages("…")`, then
`renv::snapshot()`. Both update the lockfile; commit it.

### 5. Commit and push

Open **Source Control** (the branching icon on the left, or `Ctrl+Shift+G`). Click **+** next to the
files to include, write a short message saying what you did (“Clean the date column”), and click
**Commit**. Then **Publish Branch** (the first time) or **Sync Changes**.

Commit small and often. Each commit is a version you can go back to.

### 6. Open the pull request: this is your hand-in

When the work is ready, open a pull request **from `hw1` into `main`** titled **`HW1`**:

- In VS Code: Source Control → the **Create Pull Request** icon at the top of the view, or
- on GitHub: your repository shows a **Compare & pull request** banner after you push.

In the description, write what a reviewer should look at and anything you are unsure about.
**The pull request must be open by the Monday deadline.** You can keep pushing to the branch;
new commits appear in the same pull request.

::: warning Pushing straight to `main` is not a hand-in
Work goes into `main` only through a pull request. Pushing straight to `main` is not a hand-in,
and no check runs on it. Don’t merge your own pull request either: we merge it when it is accepted.
:::

### Committed on `main` by mistake?

Look at the branch name in the bottom-left corner of VS Code.

- **You haven’t pushed yet:** create the branch now (**main** → **Create new branch…** → `hw1`).
  Your commits come along to the new branch. Publish it and open the pull request as usual.
- **You already pushed to `main`:** don’t try to undo it yourself. Tell a teacher (in a session
  or on Moodle) **before the deadline**; we’ll sort it out with you.

<!-- TODO(owner): screenshot of an open pull request with a green check. -->

### 7. Watch the check

A few minutes after you open the pull request (and after every new push), the **check** runs: a
clean computer clones your repository, installs your lockfile and renders `report.qmd`.

- **Green tick:** anyone can reproduce your report.
- **Red cross:** something works on your computer only. See [When the check is red](#when-the-check-is-red).

A red check still counts as handed in, but you must fix it.

### 8. Review, feedback, fixes

- By **Thursday**, review the classmate’s pull request you are assigned: [Review a pull request](#review-a-pull-request).
- Your reviewer and the teachers comment on your pull request. Fix what they point out by pushing
  new commits to `hw1`, and reply to each comment.

Deadlines and late rules: see [Assignments](/homework/).

## When the check is red {#when-the-check-is-red}

On the pull request, click **Details** next to the red check. Expand the step with the red cross
and read from the top down: the **first** error is the real one; later errors follow from it.

The five most common causes:

| The log says | What happened | Fix |
|---|---|---|
| `ModuleNotFoundError` / `there is no package called …` | You installed a package but it isn’t in the lockfile. | Python: `uv add <name>`. R: `renv::snapshot()`. Commit the lockfile. |
| `No such file or directory` / `cannot open file` | A file your code reads isn’t in the repository. | Commit it (check it isn’t in `.gitignore`), or commit the script that downloads it. |
| A path like `C:\Users\…` or `/Users/…` | An absolute path only exists on your computer. | Use a path relative to the repository: `data/raw/file.csv`. |
| `NameError` / `object '…' not found` | The code relied on something you ran by hand earlier. | Restart, render from scratch, and fix the order until it works. |
| `uv.lock` needs to be updated / lockfile out of sync | `pyproject.toml` changed without `uv lock`. | Run `uv lock` (or `uv add`), commit `uv.lock`. |

To see what the check sees before you push: restart, then render from scratch as in step 4.

## Review a pull request {#review-a-pull-request}

Reviewing is a skill you practise every week, and it’s required for every on-time assignment.

1. Open the classmate’s pull request on GitHub (or in VS Code’s **GitHub Pull Requests** view).
2. Read the rendered report (`report.md`) first, as a reader would. Then the **Files changed** tab.
3. Comment on specific lines: hover over a line in **Files changed**, click **+**, write your comment.
   To propose a concrete change, use a suggestion block, which the author can accept with one click:

   ````markdown
   ```suggestion
   clean <- penguins |> filter(!is.na(body_mass_g))
   ```
   ````

4. Finish with **Review changes** → a summary → **Comment**.

What to look for, in this order:

- **The science:** Is the question clear and answerable? Do the conclusions follow from the
  analysis? Are limitations stated?
- **Reproducibility:** Is the check green? Are there absolute paths, hand-edited data, missing files?
- **Clarity:** Is the report readable? Are figures labelled and explained?
- **One highlight and one concrete suggestion**, at least.

Be kind, specific and actionable: comment on the work, not the person.

## Habits

- **Never edit raw data by hand.** Every change happens in code, so anyone can see and repeat it.
- **Relative paths only.** `data/raw/file.csv`, never `C:\Users\…`.
- **Set a random seed** whenever anything is random.
- **Render from scratch before every push.** If it doesn’t render for you, it won’t for anyone.
- **One command renders everything.** No “first run this cell, then that one”.

## If your install fails {#if-your-install-fails}

Use **GitHub Codespaces** while we sort out your computer: VS Code in the browser, on a cloud
machine where everything is already installed.

1. On your repository on GitHub, click **Code** → **Codespaces** → **Create codespace on hw1**
   (or on `main`, then make the branch as in step 3).
2. Wait a minute while it installs. Then work exactly as described above, in the browser.
3. When you’re done, stop the codespace (**Codespaces** menu, bottom left → **Stop Current Codespace**)
   so it doesn’t use up your free hours.

Students get free Codespaces hours through [GitHub Education](https://education.github.com/students).
Codespaces is a fallback: bring your laptop to a session and we’ll get your own setup working.
