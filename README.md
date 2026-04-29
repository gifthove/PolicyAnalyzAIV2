# PolicyAnalyzAI V2

AI-powered policy analysis platform built on Azure, deployed via Azure DevOps pipelines and Terraform.

---

## Architecture

| Layer | Technology |
|---|---|
| API | FastAPI (Python), containerised via Docker |
| Container Registry | Azure Container Registry (ACR) |
| Hosting | Azure App Service (Linux, Docker) |
| AI | Azure OpenAI (`gpt-4.1`), Azure AI Search |
| Storage | Azure Blob Storage |
| Secrets | Azure Key Vault |
| Observability | Application Insights + Log Analytics |
| IaC | Terraform (azurerm ~>3.0) |
| CI/CD | Azure DevOps Pipelines |

---

## Repository Structure

```
.
├── .claude/
│   ├── commands/
│   │   └── branch-commit-skill.md   # /branch-commit-skill slash command
│   └── settings.local.json          # Claude Code git permissions
├── cicd/
│   ├── pipelines/
│   │   └── build-and-deploy.yml     # Main CI/CD pipeline
│   └── tf/                          # Terraform root module
│       ├── main.tf
│       ├── locals.tf
│       ├── variables.tf
│       └── modules/
│           ├── acr/
│           ├── aisearch/
│           ├── appinsights/
│           ├── appservice/
│           ├── keyvault/
│           ├── openai/
│           ├── resourcegroup/
│           └── storage/
```

---

## Prerequisites — One-Time Bootstrap

The Terraform backend (state storage) must exist before any pipeline run. Create it once manually:

```bash
az account set --subscription <your-subscription-id>

az group create -n polanalyai-state-rg -l australiaeast

az storage account create \
  -n paiv2stateacc \
  -g polanalyai-state-rg \
  --sku Standard_LRS \
  --allow-blob-public-access false

az storage container create -n polanalyai-infra-dev  --account-name paiv2stateacc
az storage container create -n polanalyai-infra-prod --account-name paiv2stateacc
```

Grant the pipeline service principal **Storage Blob Data Contributor** on `paiv2stateacc`:

```bash
az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee <pipeline-service-principal-object-id> \
  --scope /subscriptions/<your-subscription-id>/resourceGroups/polanalyai-state-rg/providers/Microsoft.Storage/storageAccounts/paiv2stateacc
```

---

## Variable Group — `PolicyAnalyzAIInfra`

The pipeline reads the following variables from the Azure DevOps Library group `PolicyAnalyzAIInfra`:

| Variable | Value | Used for |
|---|---|---|
| `AZURE_SUBSCRIPTION` | your Azure DevOps service connection name | Azure service connection name |
| `TESTERS_EMAILS` | approval email address | Prod approval gate |

---

## Pipeline — `build-and-deploy.yml`

### Stages

| Stage | Description | Condition |
|---|---|---|
| `BuildPushImages` | Publishes Terraform artifact | `DEPLOY = true` |
| `DeployBaseInfraToCI` | Terraform apply to dev environment | After build |
| `ApproveProd` | Manual approval gate | After CI passes |
| `DeployBaseInfraToPROD` | Terraform apply to prod environment | After approval |

### Trigger
- Automatic on push to `main`
- Manual via `Force Deploy?` parameter

---

## Terraform

### Resource Naming Convention

All resources follow the pattern `polanalyai-infra-<env>-<suffix>`, e.g.:
- Resource group: `polanalyai-infra-dev-rg`
- Key Vault: `polanalyai-infra-dev-kv`
- OpenAI: `polanalyai-infra-dev-oai`
- App Service: `polanalyai-infra-dev-api`

### Key Vault Access

The pipeline service principal is granted Key Vault access via an **inline `access_policy`** block inside the `azurerm_key_vault` resource. This ensures the policy exists before Terraform attempts to read or write secrets on first apply.

The web app managed identity is granted `Get`/`List` secret permissions via a separate `azurerm_key_vault_access_policy` resource in `main.tf`.

### OpenAI Deployments

| Deployment | Model | SKU |
|---|---|---|
| `text-embedding-ada-002` | text-embedding-ada-002 v2 | Standard |
| `gpt-4.1` | gpt-4.1 (2025-04-14) | GlobalStandard |

> `GlobalStandard` is required for `gpt-4.1` in the `australiaeast` region.

---

## Claude Code Slash Commands

| Command | Description |
|---|---|
| `/branch-commit-skill` | Create a new branch, stage changes, commit, and push in one step |

### Usage

```
/branch-commit-skill fix/my-branch "my commit message"
```
