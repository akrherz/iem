#!/bin/bash

# Release script for iemjs package
# Usage: ./src/release-iemjs.sh [version]
# Example: ./src/release-iemjs.sh 1.0.1

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.1"
    exit 1
fi

VERSION=$1
TAG="iemjs-v${VERSION}"

# Validate version format (basic semver check)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in semver format (e.g., 1.0.1)"
    exit 1
fi

echo "Preparing to release iemjs v${VERSION}"

# Check if we're in the right directory (should be run from repo root)
if [ ! -f "src/iemjs/package.json" ]; then
    echo "Error: Must be run from the root of the iem repository"
    echo "Current directory: $(pwd)"
    echo "Expected to find: src/iemjs/package.json"
    exit 1
fi

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working directory is not clean. Please commit or stash changes."
    git status --short
    exit 1
fi

# Update version in package.json (but don't commit yet)
cd src/iemjs
npm version $VERSION --no-git-tag-version
cd ../..

# Run basic tests
echo "Running syntax validation..."
cd src/iemjs
npm test
cd ../..

echo "Changes to be committed:"
git diff src/iemjs/package.json

read -p "Commit these changes and create tag ${TAG}? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Commit the version change
    git add src/iemjs/package.json
    git commit -m "Release iemjs v${VERSION}"
    
    # Create and push the tag
    git tag "${TAG}"
    git push origin main
    git push origin "${TAG}"
    
    echo "✅ Released iemjs v${VERSION}"
    echo "🚀 GitHub Actions will now publish to npm"
    echo "📦 Check progress at: https://github.com/akrherz/iem/actions"
    echo "📦 Package will be available at: https://www.npmjs.com/package/iemjs"
else
    # Revert the version change
    git checkout -- src/iemjs/package.json
    echo "❌ Release cancelled"
fi
