# GitHub Actions Workflows

## Automated Deployment (Optional)

The `deploy.yml` workflow is set to **manual trigger only** to avoid failures when secrets aren't configured.

### To Enable Automated Deployment:

1. **Go to your GitHub repository**: https://github.com/thesnehadas/eatmeshark
2. **Settings → Secrets and variables → Actions**
3. **Add these secrets:**
   - `VPS_HOST`: `62.72.57.117`
   - `VPS_USER`: `root` (or your SSH username)
   - `VPS_SSH_KEY`: Your private SSH key (see below)
   - `VPS_PORT`: `22` (optional, defaults to 22)

### Generate SSH Key for GitHub Actions:

**On Windows (PowerShell):**
```powershell
# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions" -f $env:USERPROFILE\.ssh\github_actions_deploy

# Copy public key to VPS (you'll need to manually add it to ~/.ssh/authorized_keys on VPS)
# Or use: type $env:USERPROFILE\.ssh\github_actions_deploy.pub | ssh root@62.72.57.117 "cat >> ~/.ssh/authorized_keys"

# Display private key to copy to GitHub secret
Get-Content $env:USERPROFILE\.ssh\github_actions_deploy
```

**On Linux/Mac:**
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_deploy
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub root@62.72.57.117
cat ~/.ssh/github_actions_deploy  # Copy this to GitHub secret
```

### Using the Workflow:

- **Manual Trigger**: Go to Actions tab → "Deploy to Hostinger VPS" → "Run workflow"
- **Automatic**: Once secrets are set, you can change `on:` to include `push:` for automatic deployment

### Note:

If you don't want to use GitHub Actions, you can simply:
1. Push code to GitHub
2. SSH into VPS
3. Run: `cd /var/www/shark-tank && git pull && systemctl restart shark-tank`

