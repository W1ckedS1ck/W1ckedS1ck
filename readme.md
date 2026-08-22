[![Profile views](https://komarev.com/ghpvc/?username=W1ckedS1ck&color=blueviolet&style=flat-square&label=Profile+views)](https://github.com/W1ckedS1ck)

# Vitali Kuts · Infrastructure / DevOps Engineer

I design, automate and operate production infrastructure end-to-end:
Terraform → Ansible → CI/CD → observability → disaster recovery.

Co-founder & CTO of **DreamSeed** — a live global social experiment with real users, accounts and payments. I own everything below the application layer.

## 🌱 Flagship: [DreamSeed Infrastructure](https://github.com/W1ckedS1ck/DreamSeed)

Production IaC powering [dreamseed.online](https://dreamseed.online) — not a demo:

- **Zero → live server in ~8 min** — one command orchestrates Terraform (AWS + Hetzner) and 17 idempotent Ansible roles across 9 playbooks
- **DR rehearsed weekly by robots** — ephemeral server: real backup → simulated disaster → restore from local *and* cloud paths → 60+ service assertions; RTO < 5 min proven in CI, not claimed in a runbook
- **11 CI gates per push** — ShellCheck, ansible-lint, Terraform lint/validate/fmt, Checkov, Trivy, Gitleaks (full history), zizmor, actionlint, pre-commit
- **Multi-region observability** — Grafana Cloud synthetic probes (3 continents) + Better Stack watchdogs + 27 local alert rules → Telegram
- **Secrets discipline** — Ansible Vault source of truth, SHA-pinned Actions, tokens never in argv, full-history leak scanning
- **Safety by design** — prod deploys behind environment gates, destroy requires typed confirmation, daily drift detection with alerts

📖 [Architecture & runbooks](https://github.com/W1ckedS1ck/DreamSeed/wiki) · 🌐 [Live status page](https://status.dreamseed.online)

## 🧰 Stack

`Terraform` · `Ansible` · `GitHub Actions` · `Bash/Python` · `AWS` · `Hetzner` · `Cloudflare` · `Grafana / VictoriaMetrics / Loki` · `MariaDB` · `Redis` · `Nginx` · `Linux hardening`

## 📚 Background

Hands-on path into infrastructure: Jenkins pipelines, Docker/Kubernetes, GitLab CI and monitoring labs (see repositories), then building and operating real production systems at DreamSeed since 2026.

<!--
Quick nav for humans: flagship repo → pinned below.
-->
