# Contributing Guidelines

We’re excited to have you contribute to **MindVirus Telegram Bot**! Before contributing, please take a moment to read these guidelines to ensure that your contributions align with our project goals and standards.

## Table of Contents
1. [Getting Started](#getting-started)
2. [How to Contribute](#how-to-contribute)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Commit Messages](#commit-messages)
5. [Pull Request Process](#pull-request-process)
6. [Issue Reporting](#issue-reporting)
7. [Community Conduct](#community-conduct)

---

## Getting Started

1. **Fork the Repository**: To start contributing, first fork the repository to your GitHub account.
2. **Clone the Fork**: Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/mindvirus-bot.git
   ```
3. **Create a Branch**: Create a feature or bugfix branch. Never work directly on the `main` branch as it is protected.
   ```bash
   git checkout -b feature/new-feature
   ```

## How to Contribute

### New Features
- Before implementing a new feature, please open an issue to discuss the idea with maintainers. This helps ensure alignment with the project’s vision.
- Once approved, follow the [Pull Request Process](#pull-request-process) below.

### Bug Fixes
- If you're fixing a bug, it’s best to open an issue first to describe the problem. This helps others validate the issue and prevents duplicated work.
- When submitting bug fixes, clearly mention the issue number in the pull request description.

### Documentation
- Contributions to documentation are highly appreciated. You can suggest improvements to the README, add setup details, or clarify existing instructions.

## Code Style Guidelines

To ensure consistency, please adhere to the following code style guidelines:
- **PEP 8**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code formatting.
- **Type Hints**: Use [type hints](https://docs.python.org/3/library/typing.html) where possible to ensure code clarity and maintainability.
- **Comments**: Ensure your code is well-documented with inline comments, docstrings, and external documentation as needed.
- **Imports**: Use Python's standard library first, followed by third-party imports, and finally local module imports. Use absolute imports wherever possible.

## Commit Messages

Please follow this structure for your commit messages:
- **Title**: A concise summary of the change (50 characters max)
- **Body**: Detailed explanation of the change, including the problem and the solution.
- **Issue Reference**: Include the issue number being addressed (e.g., `Fixes #45`).

Example:
```
Add mini-feed grouping feature

This commit introduces a new feature that allows users to group related 
Instagram posts into mini-feeds, improving content organization.

Fixes #45
```

## Pull Request Process

1. **Testing**: Before submitting a pull request, ensure all new and existing tests pass. Add new tests if your changes introduce new functionality.
2. **Opening a PR**: Once your work is ready, push the branch to your fork and submit a pull request:
   ```bash
   git push origin feature/new-feature
   ```
3. **Describe the PR**: Clearly describe the purpose of your pull request. Mention the issue number it addresses (if applicable) and detail what changes are made.
4. **Request Reviews**: Your pull request will automatically be reviewed. We require at least one approved review before merging. The `main` branch is protected and only maintainers can merge changes.
5. **CI/CD Checks**: The CI pipeline will run checks on your pull request. All tests must pass before your pull request can be merged.

## Issue Reporting

If you encounter a bug or have a feature request, follow these steps:
1. **Search Existing Issues**: Before opening a new issue, please search the [issues list](https://github.com/yourusername/mindvirus-bot/issues) to see if the problem or request has already been reported.
2. **Create a New Issue**: If it’s a new problem, click on the "New Issue" button and provide as much detail as possible, including:
   - A descriptive title
   - Steps to reproduce the issue
   - Expected behavior
   - Screenshots or code snippets (if applicable)

## Community Conduct

We value respect, collaboration, and inclusivity in our community. Please be courteous to others and avoid any form of disrespect or harassment. For more details, see our [Code of Conduct](CODE_OF_CONDUCT.md).
