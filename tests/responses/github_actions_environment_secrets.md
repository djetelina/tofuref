---
layout: "github"
page_title: "GitHub: github_actions_environment_secrets"
description: |-
  Reads GitHub Actions secrets within a GitHub repository environment
---

# github_actions_environment_secrets

This data source allows you to read GitHub Actions secrets defined within your GitHub repository environments.

Secret values are encrypted and stored securely by GitHub, so this data source exposes only metadata such as timestamps and ids.

## Example Usage

```hcl
data "github_actions_environment_secrets" "example" {
  repository  = "my-org/my-repo"
  environment = "production"
}
```
