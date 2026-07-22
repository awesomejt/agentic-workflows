#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${WORKFLOWS_TARGET:-workstation}"

exec "${repo_root}/bin/workflowctl" deploy --target "${target}" "$@"
