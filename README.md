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
./bin/autofix.sh --fixer labels --help
./bin/autofix.sh --fixer syncfile --help
```

# Examples

```bash
./bin/autofix.sh --fixer syncfile -i --limit 1
  --apply-changes
  --allow-missing
  --src a.txt
  --dst b.txt
```

```bash
all-repos-sed --dry-run --limit 1 \
'/labels:/,$d' .github/settings.yml \
--commit-msg 'Remove labels from settings file'
```
