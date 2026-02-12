# Guidance for AI coding assistants (repo: master)

This repository is a tooling/infrastructure collection (not a single web app). The goal of these notes is to give an AI coding agent quick, actionable facts so it can be productive without guessing repo conventions.

Key structure (top-level folders)
- `Ansible/` — playbooks and an inventory (e.g., `Ansible/get_version.yml`, `Ansible/set_motd.yml`, `Ansible/inventory.yml`). These are executed with `ansible-playbook -i Ansible/inventory.yml <playbook>`.
- `Docker/` — several example stacks. Notable ones:
  - `Docker/GrafanaPrometheus/` — contains `docker-compose.yml` and `README` which instructs `docker-compose up -d` and Grafana/Prometheus URLs.
  - `Docker/BasicNode/` — small Node app with `package.json` (run `npm install` then `npm start`).
- `Python/` — collection of standalone scripts (not a packaged Python module). Examples:
  - `Python/nist_vuln_checker.py` — a script that queries NVD, reads `Python/test_data/productlist.csv`, and writes `Python/test_data/cves.xlsx`. It uses packages that must be pip-installed (e.g., `requests`, `packaging`, `xlsxwriter`).
  - `Python/Checkpoint/` — ad-hoc automation scripts for Check Point devices (e.g., `add_host_to_cluster.py`, `change_backup_server.py` — note: some files may be empty/placeholders).
- `Terraform/` — subfolders for different providers/services (e.g., `Terraform/VMware/`, `Terraform/Checkpoint*`). Some `.tfstate` files are present in the repo — treat them as potentially sensitive.
- `Powershell/` and `Windows/` — Windows/Powershell scripts and Terraform state relevant to Windows.

Concrete, repo-discoverable workflows
- Run Grafana/Prometheus stack: `cd Docker/GrafanaPrometheus; docker-compose up -d` (see `Docker/GrafanaPrometheus/README`).
- Run BasicNode: `cd Docker/BasicNode; npm install; npm start` (service entrypoint is `app.js`).
- Run Ansible playbooks: `ansible-playbook -i Ansible/inventory.yml Ansible/get_version.yml`.
- Run Python scripts: use a venv and pip-install required packages. Example: `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install requests packaging xlsxwriter` then `python Python/nist_vuln_checker.py` (script uses `Python/test_data/productlist.csv`).
- Terraform: operate inside each subfolder (e.g., `Terraform/VMware`) with the normal `terraform init/plan/apply` flow. Note: `.tfstate` files are already present — do not overwrite or commit credentials.

Project conventions & patterns an agent should respect
- This repo groups examples/tools by technology (Ansible/Docker/Python/Terraform). When making changes, keep edits within the appropriate folder and avoid cross-cutting refactors unless requested.
- Python scripts are written as standalone CLI scripts (no package layout). Prefer minimal, backwards-compatible edits (small helper functions, add tests if requested, but don't convert entire folder into a package without user approval).
- Inputs are often file-based (see `Python/test_data/` with `productlist.csv` and JSON sample outputs). Use those files as examples for expected data formats.
- Where a script references a pip package in comments (e.g., `# pip install packaging`), assume there is no requirements.txt and surface a suggestion to add one if you introduce new dependencies.

Integration points & external dependencies
- NVD API: `Python/nist_vuln_checker.py` calls `https://services.nvd.nist.gov/`.
- Docker stacks: local docker/docker-compose network; Grafana and Prometheus communicate over the compose network (see `prometheus.yml` in `Docker/GrafanaPrometheus`).
- Checkpoint scripts likely expect network/API access to Check Point appliances — changes to those scripts should be made mindful of credentials and live-device impacts.

Editing guardrails (safety and verification)
- There are no unit tests present; prefer small, reviewable changes and add a brief manual verification step in any PR (e.g., how to run a script locally and expected sample output path).
- Avoid committing secrets, credentials, or `.tfstate` changes. If you need to handle secrets, prefer adding a README note and ask the human for secure values.
- When modifying Terraform folders, run `terraform plan` in the same folder to confirm intended changes before apply.

Examples to reference in pull requests
- “Fixed CSV parsing bug in `Python/nist_vuln_checker.py` — tested locally by running `python Python/nist_vuln_checker.py` with `Python/test_data/productlist.csv` and verifying `Python/test_data/cves.xlsx` is produced.”
- “Updated `Docker/GrafanaPrometheus/docker-compose.yml` network settings — verified with `docker-compose up -d` and Grafana reachable at http://localhost:3000 per `Docker/GrafanaPrometheus/README`.”

If something is unclear, ask the repo owner for: 1) desired CI/build conventions, 2) whether to add a `requirements.txt` for Python, and 3) handling of existing `.tfstate` files.

---
Please review this file and tell me if you'd like more detail about any specific subfolder (Ansible, a particular Python script, or a Terraform workspace) or if you'd prefer I add quick run/test commands for a particular component.
