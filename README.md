# About

See the https://github.com/asottile/all-repos project.

# Setup

```bash
# Install all-repos somehow...
pipx install all-repos
# Configure all-repos.json
touch all-repos.json
# Clone repositories
all-repos-clone
```

# Usage

```bash
./bin/autofix.sh --help
./bin/autofix.sh --fixer base --help
./bin/autofix.sh --fixer bcomp --help
./bin/autofix.sh --fixer editPR --help
./bin/autofix.sh --fixer labels --help
./bin/autofix.sh --fixer syncfile --help
```

# Examples

## Loop PRs and approve and/or merge them interactively

```bash
./bin/approve.sh --search "Bump OR automatic"
```

## Copy file into repo

```bash
./bin/autofix.sh --fixer syncfile -i --limit 1
  --apply-changes
  --allow-missing
  --src a.txt
  --dst b.txt
```

## Open diff tool for file

```bash
./bin/autofix.sh --fixer bcomp -i --limit 1
  --apply-changes
  --allow-missing
  --branch add-pr-template
  --message "Add PR template"
  --src pull_request_template.md
  --dst .github/pull_request_template.md
```

## Edit PRs with the given branch

```bash
./bin/autofix.sh --fixer editPR -i --limit 1
  --apply-changes
  --branch add-pr-template
  --add-label "DoNotMerge"
  --add-assignee '@me'
  --add-reviewer "@other"
```

## Run sed command on files

```bash
all-repos-sed --dry-run --limit 1 \
'/labels:/,$d' .github/settings.yml \
--commit-msg 'Remove labels from settings file'
```
