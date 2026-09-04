# Releasing exptoolkit to PyPI

This document explains how to publish a new version of `exptoolkit` while working in VS Code.

Open the repository folder in VS Code and run the commands below in its integrated PowerShell terminal. Use the Source Control view to review changes before committing. CI results and release approval are handled on GitHub in a web browser.

## Publish a new version

The examples below use version `0.3.1`. Replace it with the version you want to publish.

### 1. Update and check the version

In the VS Code terminal, start from a clean, up-to-date `main` branch:

```powershell
git switch main
git pull --ff-only origin main
git status
uv version 0.3.1
uv version --short
uv lock --check
```

Review `pyproject.toml` and `uv.lock` in the VS Code Source Control view. A normal version update should change only these two files.

### 2. Run local checks

```powershell
uv sync --locked --all-extras
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run tox
```

Do not continue until these checks pass.

### 3. Commit and push the version

```powershell
git add pyproject.toml uv.lock
git commit -m "Bump version to 0.3.1"
git push origin main
```

Open **GitHub -> Actions -> CI** in your browser and wait for all six checks to pass.

### 4. Create the release tag

The tag must be `v` followed by the exact project version.

```powershell
git tag -a v0.3.1 -m "v0.3.1"
git push origin v0.3.1
```

This starts the Release workflow.

### 5. Review and approve the release

Open **GitHub -> Actions -> Release** in your browser.

Wait for **Build and verify distributions** to pass. Then open the waiting PyPI deployment, select the `pypi` environment, and choose **Approve and deploy**.

Approval publishes the release to PyPI. Check the new version at:

<https://pypi.org/project/exptoolkit/>

Confirm that both the wheel and source distribution are present.

## What the workflows do

### CI

CI runs for every pull request and every push to `main`. It checks:

- tests on Python 3.9 through 3.13;
- tests with all optional dependencies on Python 3.13;
- Ruff lint and formatting;
- mypy type checking.

### Release

Pushing a tag such as `v0.3.1` starts the release checks. The workflow:

- confirms that the tag matches the project version;
- runs the Python 3.9 tests;
- builds a wheel and source distribution;
- checks metadata and package contents;
- checks that `py.typed` and the license are included;
- checks that unwanted files and `batanalysis` are absent;
- installs and imports both distributions;
- waits for manual approval;
- publishes the checked files to PyPI.

GitHub authenticates to PyPI with Trusted Publishing. No PyPI API token is stored in the repository or GitHub Secrets. The build and publish jobs are separate, and publishing uses the files that passed the release checks.

Creating a GitHub Release is optional and separate from publishing to PyPI.

## Current publishing settings

The GitHub environment is named `pypi`. Its required reviewer is `t-onoz`, and self-review is allowed for this one-person project.

The PyPI Trusted Publisher has these values:

| Field | Value |
| --- | --- |
| Owner | `t-onoz` |
| Repository | `exptoolkit` |
| Workflow | `release.yml` |
| Environment | `pypi` |

These values must match exactly.

## Official documentation

- [Using uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
- [Building and publishing with uv](https://docs.astral.sh/uv/guides/package/)
- [Adding a Trusted Publisher to an existing PyPI project](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
- [GitHub deployment environments and approvals](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)

## Troubleshooting

- **CI fails:** Open the first failed step and read its error. Fix the cause before tagging a release.
- **Release does not start:** Confirm that the tag was pushed and looks like `v0.3.1`.
- **Version check fails:** Make the tag exactly match the version reported by `uv version --short`.
- **Publish is waiting:** This is expected. Approve the `pypi` environment deployment in GitHub.
- **Trusted Publishing fails:** Check the four publisher values in the table above. Do not add a long-lived token as a quick workaround.
- **PyPI says the version exists:** Published versions cannot be replaced. Use a new version.
- **Only one file was uploaded:** Retry the failed publish job from the same workflow run. Do not rebuild the files under the same version.

When asking an AI assistant for help, copy the failed GitHub Actions step and relevant log, then include the tag and commit SHA. State whether anything was published. Never paste tokens, credentials, cookies, recovery codes, or private keys. Ask for diagnosis first and explicitly say not to publish, push, or change tags without permission.
