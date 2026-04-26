# PolicyAnalyzAI v2 — Phase 1: Skill + Project Setup

## Context

Building PolicyAnalyzAI v2, a production-style RAG system on Azure. The old project (GPT-2 fine-tuning) lives at `C:\Users\gifth\Downloads\PolicyAnalyzAI-main\`. Phase 1 creates the new project skeleton with a reusable skill so it can be re-run or shared.

## Approach

Create a `/policyanalyzai-setup` skill that scaffolds the whole project when invoked. This makes the setup repeatable and documents every step.

## Current State (already installed — nothing to install)

| Tool      | Status                    |
|-----------|---------------------------|
| Python    | 3.12.7 @ `C:\Python3`    |
| pip       | 25.0.1                    |
| Docker    | ✓                         |
| Terraform | ✓ (via Chocolatey)        |
| Azure CLI | ✓                         |
| venv      | ✓ (stdlib)                |

## Step 1 — Create the skill

**Skill file location:**
`C:\Users\gifth\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin\5dfaaab4-6521-45ce-8bf9-d3d3e4dc0cc2\236dd38c-f210-4ef6-8c07-d93baeb46562\skills\policyanalyzai-setup\SKILL.md`

**Skill content:**

```
---
name: policyanalyzai-setup
description: >
  Scaffolds the PolicyAnalyzAI v2 project Phase 1 on Windows. Creates the full
  directory structure (app, infra, tests, docs, scripts, pipelines, prompts),
  sets up a Python 3.12 virtual environment using C:\Python3, installs FastAPI
  + uvicorn + python-dotenv, generates the /health endpoint, .env.example,
  .gitignore, requirements.txt, and a Terraform bootstrap skeleton in
  infra/bootstrap/. Invoke when the user types /policyanalyzai-setup, asks to
  scaffold PolicyAnalyzAI, or wants to set up the Phase 1 RAG project.
---

# PolicyAnalyzAI v2 — Phase 1 Setup

## Prerequisites (already on this machine)
- Python 3.12.7 at C:\Python3
- Docker, Terraform (Chocolatey), Azure CLI, Git

## Step 1: Directories

```bash
mkdir -p C:/Development/PolicyAnalyzAIV2/{app/routes,app/services,infra/bootstrap,infra/environments/dev,tests,docs,scripts,pipelines,prompts}
touch C:/Development/PolicyAnalyzAIV2/app/__init__.py C:/Development/PolicyAnalyzAIV2/app/routes/__init__.py C:/Development/PolicyAnalyzAIV2/app/services/__init__.py
```

## Step 2: Virtual environment

```bash
C:/Python3/python.exe -m venv C:/Development/PolicyAnalyzAIV2/.venv
C:/Development/PolicyAnalyzAIV2/.venv/Scripts/pip install fastapi "uvicorn[standard]" python-dotenv pytest httpx
C:/Development/PolicyAnalyzAIV2/.venv/Scripts/pip freeze > C:/Development/PolicyAnalyzAIV2/requirements.txt
```

## Step 3: App files

### app/main.py
from fastapi import FastAPI
from app.routes.health import router as health_router

app = FastAPI(title="PolicyAnalyzAI v2")
app.include_router(health_router)

### app/routes/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

### app/config.py
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "")
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING", "")
APP_ENV = os.getenv("APP_ENV", "dev")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

## Step 4: .env.example

AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_KEY=
AZURE_BLOB_CONNECTION_STRING=
APP_ENV=dev
LOG_LEVEL=INFO

## Step 5: .gitignore

.venv/
.env
__pycache__/
*.pyc
*.pyo
**/.terraform/
*.tfstate
*.tfstate.backup
.terraform.lock.hcl
*.egg-info/
dist/
build/
.pytest_cache/

## Step 6: Terraform bootstrap (infra/bootstrap/)

### infra/bootstrap/main.tf
terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.0" }
  }
}

provider "azurerm" { features {} }

resource "azurerm_resource_group" "tfstate" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "tfstate" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.tfstate.name
  location                 = azurerm_resource_group.tfstate.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}

### infra/bootstrap/variables.tf
variable "resource_group_name" { default = "rg-policyanalyzai-tfstate" }
variable "storage_account_name" {
  description = "Globally unique, 3-24 lowercase alphanumeric chars"
  type        = string
}
variable "location" { default = "australiaeast" }

### infra/bootstrap/outputs.tf
output "storage_account_name" { value = azurerm_storage_account.tfstate.name }
output "container_name"       { value = azurerm_storage_container.tfstate.name }

## Step 7: Minimal test (tests/test_health.py)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

## Step 8: Git init

```bash
cd C:/Development/PolicyAnalyzAIV2
git init
git add .
git commit -m "Phase 1: PolicyAnalyzAI v2 scaffold — FastAPI shell, venv, Terraform bootstrap"
```

## Verification

Run:  C:/Development/PolicyAnalyzAIV2/.venv/Scripts/uvicorn app.main:app --reload
Open: http://localhost:8000/health  → {"status": "ok"}
Open: http://localhost:8000/docs   → Swagger UI
```

## Step 2 — Run the skill immediately

After creating the skill file, execute all steps from the skill to scaffold `C:\Development\PolicyAnalyzAIV2\` right now.

Also copy this plan file into the project as `C:\Development\PolicyAnalyzAIV2\docs\phase1-plan.md` so it travels with the repo.

## Files to create

| File | Purpose |
|------|---------|
| `.../skills/policyanalyzai-setup/SKILL.md` | Reusable skill |
| `C:\Development\PolicyAnalyzAIV2\app\main.py` | FastAPI entry point |
| `C:\Development\PolicyAnalyzAIV2\app\routes\health.py` | /health endpoint |
| `C:\Development\PolicyAnalyzAIV2\app\config.py` | dotenv settings |
| `C:\Development\PolicyAnalyzAIV2\.env.example` | env template |
| `C:\Development\PolicyAnalyzAIV2\requirements.txt` | pinned deps |
| `C:\Development\PolicyAnalyzAIV2\infra\bootstrap\main.tf` | Terraform state bootstrap |
| `C:\Development\PolicyAnalyzAIV2\infra\bootstrap\variables.tf` | |
| `C:\Development\PolicyAnalyzAIV2\infra\bootstrap\outputs.tf` | |
| `C:\Development\PolicyAnalyzAIV2\.gitignore` | Python + Terraform ignores |
| `C:\Development\PolicyAnalyzAIV2\tests\test_health.py` | Health check test |
| `C:\Development\PolicyAnalyzAIV2\docs\phase1-plan.md` | This plan, copied into the repo |

## Verification

1. `C:/Development/PolicyAnalyzAIV2/.venv/Scripts/uvicorn app.main:app --reload`
2. `http://localhost:8000/health` → `{"status": "ok"}`
3. `http://localhost:8000/docs` → Swagger UI loads
