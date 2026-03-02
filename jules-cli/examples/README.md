# Jules CLI — Examples

## Minimal Prompt Pack

1. Copy `minimal-pack/` to a temp folder (e.g. `C:\temp\jules_pack`).
2. Edit:
   - `PACK.md` (task list + status)
   - `tasks/TASK-EXAMPLE-REV.md` (repo/branch/scope/paths/output placement)
3. From the `jules-cli/` directory, dispatch:

```powershell
python scripts/dispatch_prompt_pack.py `
  --pack-dir C:\temp\jules_pack `
  --repo <owner/repo> `
  --starting-branch <branch>
```

4. Monitor status:

```powershell
python scripts/jules_bridge.py --json status --session-id <id>
```

Notes:
- For multi-task batches, set `JULES_API_KEY` to avoid CLI ghost-session risks (see `scripts/dispatch_prompt_pack.py` gates).
- If using `plan-doc-editor`, set Document Placement to `<plan_module>/investigation/` and return `Plan Update Targets` for write-back.

