#!/bin/bash

# Script to remove trailing whitespaces from all text files in the project

echo "Removing trailing whitespaces from project files..."

# Find and clean Python files
find . -type f -name "*.py" -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -exec sed -i '' 's/[[:space:]]*$//' {} \;

# Find and clean Markdown files
find . -type f -name "*.md" -not -path "./.git/*" -exec sed -i '' 's/[[:space:]]*$//' {} \;

# Find and clean text files
find . -type f -name "*.txt" -not -path "./.git/*" -exec sed -i '' 's/[[:space:]]*$//' {} \;

# Find and clean YAML files
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -not -path "./.git/*" -exec sed -i '' 's/[[:space:]]*$//' {} \;

# Find and clean JSON files
find . -type f -name "*.json" -not -path "./.git/*" -not -path "./Pipfile.lock" -exec sed -i '' 's/[[:space:]]*$//' {} \;

# Clean other important files
for file in Pipfile Dockerfile .gitignore README.md; do
    if [ -f "$file" ]; then
        sed -i '' 's/[[:space:]]*$//' "$file"
    fi
done

echo "✓ Trailing whitespaces removed successfully!"

# Optional: Check if any files still have trailing whitespaces
echo ""
echo "Checking for any remaining trailing whitespaces..."
remaining=$(grep -r '[[:space:]]$' --include="*.py" --include="*.md" --include="*.txt" --include="*.yml" --include="*.yaml" --exclude-dir=".git" --exclude-dir="venv" --exclude-dir=".venv" . 2>/dev/null | wc -l)

if [ "$remaining" -eq 0 ]; then
    echo "✓ No trailing whitespaces found!"
else
    echo "⚠ Found $remaining lines with trailing whitespaces"
    echo "Run 'grep -r \"[[:space:]]$\" --exclude-dir=\".git\" .' to see them"
fi
