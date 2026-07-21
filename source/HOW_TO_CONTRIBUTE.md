# How to Use GitHub to Contribute to the AIMA Project

This guide is for contributors who are new to Git or GitHub. It walks you through the workflow we use and offers alternatives for contributors who prefer working in Word or other formats.

## Quick Overview of the Contribution Flow

1. Create a GitHub account (if you don’t have one).
2. Fork the repository to your own GitHub space.
3. Make edits (in-browser or on your local machine).
4. Create a Pull Request (PR) to propose your changes.
5. Get feedback and iterate if needed.
6. Once approved, your contribution will be merged into the project.

You can sync your repository regularly to get all the changes from others. 
To avoid merge-conflicts, it is advised to check (via Slack) if anyone else is already working on the files you 
plan on editing. 

## Step-by-Step Instructions

### 1. Fork the Repository

- Go to the [AIMA GitHub repo](https://github.com/OWASP/www-project-ai-maturity-assessment).
- Click the “Fork” button (top right). This creates a personal copy of the project under your GitHub account.

### 2. Make Edits (Option A: GitHub Web UI – No Git Required)

- Navigate to your forked copy.
- Browse to the folder you'd like to contribute to: `source/latest/...`
- Click the file (e.g., `20_Example_Section.md`) and choose “Edit this file.”
- Make your changes using Markdown syntax.
- Scroll down and write a short summary of your change.
- Select “Commit directly to the `main` branch.”

This is the recommended method for small text changes or new sections.

### 2. Make Edits (Option B: Local Checkout – For Advanced Users)

If you’re comfortable with Git:

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/www-project-ai-maturity-assessment.git
cd AIMA

# Make sure you're on the main branch
git checkout main

# Make edits locally (in Markdown)
# Follow the file and folder naming conventions

# Commit and push
git add .
git commit -m "Added section on XYZ"
git push origin main
```

Then, go to your GitHub fork and open a Pull Request to the original repository’s `main` branch.

## What if I Don’t Want to Use GitHub at All?

If you’d prefer to write your section in Word or plain text, that’s totally fine. Reach out to @Philippe on Slack and
let's coordinate.

We want to support contributors of all technical levels.

## Pull Request Best Practices

Once you’ve created a pull request:

- Keep each PR focused: one section or one set of changes.
- Add a short description of what you changed and why.
- If your change affects file names, structure, or numbering — discuss first on Slack.
- Be patient with feedback. We aim for a collaborative tone.

## Optional: GitHub Desktop or VS Code

If you're a bit more curious but not ready for command-line Git, you can use:

- [GitHub Desktop](https://desktop.github.com/) – A GUI to manage your fork and branches.
- [VS Code](https://code.visualstudio.com/) with the GitHub extension.

## Learn More

- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Docs: Forking a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
- Ask for help in the [#project-aima](https://owasp.slack.com/archives/C089K6KFZMG) Slack.
