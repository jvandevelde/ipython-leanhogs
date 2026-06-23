#!/bin/bash

# coi build --profile jules-default
## creates incus image coi-jules-default
# coi shell --profile jules-default

#apt-get update 
#apt-get install -y jq

export HOME="/home/code"
curl -sSL https://raw.githubusercontent.com/lukaszraczylo/claude-mnemonic/main/scripts/install.sh | bash

cat << EOF > /home/code/.claude/settings.local.json
{
  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "medium"
  },
  "permissions": {
    "defaultMode": "bypassPermissions",
    "skipDangerousModePermissionPrompt": true
  },
  "effortLevel": "medium",
  "allowDangerouslySkipPermissions": true,
  "bypassPermissionsModeAccepted": true,
  "effortCalloutDismissed": true,
  "effortLevelAccepted": true,
  "hasSeenEffortPrompt": true,
  "skipDangerousModePermissionPrompt": true,
  "enabledPlugins": {
    "claude-mnemonic@claude-mnemonic": true
  },
  "statusLine": {
    "type": "command",
    "command": "/home/code/.claude/plugins/marketplaces/claude-mnemonic/hooks/statusline",
    "padding": 0
  },
  "mcpServers": {
    "claude-mnemonic": {
      "command": "/home/code/.claude/plugins/marketplaces/claude-mnemonic/mcp-server",
      "args": [
        "--project",
        "${CLAUDE_PROJECT}"
      ],
      "env": {}
    }
  }
}
EOF

chown -R code:code /home/code/.claude-mnemonic/

cat << EOF > /home/code/mnemonic.sh
#!/bin/bash

nohup /home/code/.claude/plugins/cache/claude-mnemonic/claude-mnemonic/v0.14.9/worker > /tmp/claude-mnemonic-worker.log 2>&1 &
EOF

chmod 777 /home/code/mnemonic.sh
chown code:code /home/code/mnemonic.sh

cat << EOF > /etc/systemd/system/mnemonic.service
[Unit]
Description=Mnemonic
After=network.target

[Service]
Type=simple
ExecStart=/home/code/mnemonic.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# nohup /home/code/.claude/plugins/cache/claude-mnemonic/claude-mnemonic/v0.14.9/worker > /tmp/claude-mnemonic-worker.log 2>&1 &