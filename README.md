# PolicyAnalyzAI V2

AI-powered policy analysis platform built on Azure, deployed via Azure DevOps pipelines and Terraform.

---

## Architecture

| Layer              | Technology                                 |
|--------------------|--------------------------------------------|
| API                | FastAPI (Python), containerised via Docker |
| Container Registry | Azure Container Registry (ACR)             |
| Hosting            | Azure Container Apps (Linux, Docker)       |
| AI                 | Azure OpenAI (`gpt-4.1`), Azure AI Search  |
| Storage            | Azure Blob Storage                         |
| Secrets            | Azure Key Vault                            |
| Observability      | Application Insights + Log Analytics       |
| IaC                | Terraform (azurerm ~>3.0)                  |
| CI/CD              | Azure DevOps Pipelines                     |

---

## Repository Structure

```
.
├── api/                             # FastAPI backend
│   ├── app/                         # Python package
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── schemas/
│   ├── tests/                       # pytest test suite
│   ├── Dockerfile                   # Container image definition
│   ├── pytest.ini                   # pytest config (pythonpath = . relative to api/)
│   ├── requirements.txt
│   └── .env.example
├── ui/                              # React SPA frontend (not yet scaffolded)
├── docs/
│   └── phase1-plan.md
├── .claude/
│   ├── commands/
│   │   └── branch-commit-skill.md   # /branch-commit-skill slash command
│   ├── settings.json                # Claude Code shared settings
│   └── settings.local.json          # Claude Code git permissions
├── cicd/
│   ├── pipelines/
│   │   ├── api-build-and-deploy.yml   # API CI/CD pipeline (build, push, deploy)
│   │   ├── infra-build-and-deploy.yml # Infra (Terraform) deploy pipeline
│   │   ├── destroy-infra.yml          # Infra teardown (manual, gated)
│   │   └── templates/
│   │       └── job-deploy-infra.yml   # Shared Terraform deploy job template
│   └── tf/                          # Terraform root module
│       ├── main.tf
│       ├── locals.tf
│       ├── variables.tf
│       ├── variables/
│       │   ├── dev.tfvars
│       │   └── prod.tfvars
│       └── modules/
│           ├── acr/
│           ├── aisearch/
│           ├── appinsights/
│           ├── containerapp/
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

| Variable              | Value                                     | Used for                      |
|-----------------------|-------------------------------------------|-------------------------------|
| `AZURE_SUBSCRIPTION`  | your Azure DevOps service connection name | Azure service connection name |
| `TESTERS_EMAILS`      | approval email address                    | Prod approval gate            |

---

## Pipeline — `api-build-and-deploy.yml`

CI/CD pipeline for the FastAPI app. Triggers automatically on pushes and PRs to `main` that touch `api/**` or the pipeline file itself.

### Stages

| Stage             | Description                                                   | Condition                       |
|-------------------|------------------------------------------------------------------|------------------------------------|
| `BuildAndTest`    | Installs dependencies, runs pytest, publishes results            | Always                              |
| `PublishToDocker` | `docker build` + `docker push` of `api/` to `$(DEV_ACR_NAME)`     | Tests pass, not a PR                |
| `DeployToDev`     | `az containerapp update` on the dev Container App                | After image pushed                  |
| `ApproveProd`     | Manual approval gate (emails from `TESTERS_EMAILS`)               | After dev deploy                    |
| `DeployToProd`    | `az acr import` into prod ACR + `az containerapp update`          | After approval                      |

### Trigger
- Push or PR to `main`, filtered to changes under `api/**` or this pipeline file

### Container App Targets

| Environment | ACR                 | Container App               | Resource Group              |
|-------------|---------------------|------------------------------|------------------------------|
| Dev  | `polanalyaidevacr`  | `polanalyai-infra-dev-api`  | `polanalyai-infra-dev-rg`  |
| Prod | `polanalyaiprodacr` | `polanalyai-infra-prod-api` | `polanalyai-infra-prod-rg` |

To get the live URL of a Container App:

```bash
az containerapp show -n polanalyai-infra-dev-api -g polanalyai-infra-dev-rg \
  --query properties.configuration.ingress.fqdn -o tsv
```

---

## Pipeline — `infra-build-and-deploy.yml`

Manually triggered pipeline that publishes `cicd/tf` as an artifact and runs `terraform apply` for dev/CI then prod via the shared `templates/job-deploy-infra.yml` job template.

### Parameters

| Parameter | Default | Description                                                         |
|-----------|---------|----------------------------------------------------------------------|
| `DEPLOY`  | `false` | Force the deploy stages to run on a non-`main` branch. Always runs on `main`. |

### Stages

| Stage                   | Description                                                                                          | Condition        |
|-------------------------|---------------------------------------------------------------------------------------------------------|----------------------|
| `BuildPushImages`       | Publishes `cicd/tf` as the `tf` pipeline artifact                                                       | `DEPLOY == true`     |
| `DeployBaseInfraToCI`   | `terraform apply -var-file=variables/dev.tfvars` against the `polanalyai-infra-dev` state container    | After publish        |
| `ApproveProd`           | Manual approval gate (emails from `TESTERS_EMAILS`)                                                     | After CI deploy      |
| `DeployBaseInfraToPROD` | `terraform apply -var-file=variables/prod.tfvars` against the `polanalyai-infra-prod` state container  | After approval       |

### Trigger
- Manual only (`trigger: none`) — run from Azure DevOps Pipelines UI

---

## Pipeline — `destroy-infra.yml`

Manually triggered, double-confirmed Terraform teardown for a single environment.

### Parameters

| Parameter     | Default   | Values        | Description                                                                  |
|---------------|-----------|---------------|---------------------------------------------------------------------------------|
| `ENVIRONMENT` | `dev`     | `dev`, `prod` | Environment to destroy                                                          |
| `CONFIRM`     | _(empty)_ | any string    | Must exactly match `ENVIRONMENT`, or the run fails before anything is destroyed |

### Stages

| Stage            | Description                                                                                                                       |
|------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `ConfirmDestroy` | Fails the run unless `CONFIRM` equals `ENVIRONMENT`                                                                              |
| `DestroyInfra`   | `terraform init` against the env's state container, then `terraform destroy -auto-approve`, then fallback `az cognitiveservices account purge` / `az keyvault purge` for any soft-deleted resources |

`DestroyInfra` runs as a `deployment` job against the Azure DevOps environment `policyanalyzai-destroy-<ENVIRONMENT>` — add approval checks there for an extra human gate, especially for `prod`.

### Trigger
- Manual only (`trigger: none`)

---

## Terraform

### Resource Naming Convention

All resources follow the pattern `polanalyai-infra-<env>-<suffix>`, e.g.:
- Resource group: `polanalyai-infra-dev-rg`
- Key Vault: `polanalyai-infra-dev-kv`
- OpenAI: `polanalyai-infra-dev-oai`
- Container App: `polanalyai-infra-dev-api`

### Key Vault Access

The pipeline service principal is granted Key Vault access via an **inline `access_policy`** block inside the `azurerm_key_vault` resource. This ensures the policy exists before Terraform attempts to read or write secrets on first apply.

The Container App's managed identity is granted `Get`/`List` secret permissions via a separate `azurerm_key_vault_access_policy` resource in `main.tf`.

### OpenAI Deployments

| Deployment                | Model                     | SKU              |
|---------------------------|---------------------------|------------------|
| `text-embedding-ada-002`  | text-embedding-ada-002 v2 | Standard         |
| `gpt-4.1`                 | gpt-4.1 (2025-04-14)      | GlobalStandard   |

> `GlobalStandard` is required for `gpt-4.1` in the `australiaeast` region.

---

## Claude Code Slash Commands

| Command                | Description                                                      |
|------------------------|------------------------------------------------------------------|
| `/branch-commit-skill` | Create a new branch, stage changes, commit, and push in one step |

### Usage

```
/branch-commit-skill fix/my-branch "my commit message"
```
