// PM2 ecosystem config for CLOUD deployment (GCP e2-micro)
// Only lightweight processes - no Playwright/browser-based services
// Usage: pm2 start ecosystem.cloud.config.js
module.exports = {
  apps: [
    {
      name: 'main-processor',
      script: './src/main.py',
      interpreter: 'python3',
      cwd: '/app',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault',
        GOLD_TIER_ENABLED: 'true',
        DEPLOYMENT_MODE: 'cloud'
      },
      error_file: './logs/main-processor-error.log',
      out_file: './logs/main-processor-out.log',
      log_file: './logs/main-processor-combined.log',
      time: true
    },
    {
      name: 'file-system-watcher',
      script: './src/watchers/file_system_watcher.py',
      interpreter: 'python3',
      cwd: '/app',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault',
        DEPLOYMENT_MODE: 'cloud'
      },
      error_file: './logs/file-system-watcher-error.log',
      out_file: './logs/file-system-watcher-out.log',
      log_file: './logs/file-system-watcher-combined.log',
      time: true
    },
    {
      name: 'gmail-watcher',
      script: './src/watchers/gmail_watcher.py',
      interpreter: 'python3',
      cwd: '/app',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault',
        DEPLOYMENT_MODE: 'cloud'
      },
      error_file: './logs/gmail-watcher-error.log',
      out_file: './logs/gmail-watcher-out.log',
      log_file: './logs/gmail-watcher-combined.log',
      time: true
    },
    {
      name: 'linkedin-watcher',
      script: './src/watchers/linkedin_watcher.py',
      interpreter: 'python3',
      cwd: '/app',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault',
        DEPLOYMENT_MODE: 'cloud'
      },
      error_file: './logs/linkedin-watcher-error.log',
      out_file: './logs/linkedin-watcher-out.log',
      log_file: './logs/linkedin-watcher-combined.log',
      time: true
    },
    {
      name: 'health-server',
      script: './deploy/health_check.py',
      interpreter: 'python3',
      cwd: '/app',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault',
        DEPLOYMENT_MODE: 'cloud',
        HEALTH_PORT: '8080'
      },
      error_file: './logs/health-server-error.log',
      out_file: './logs/health-server-out.log',
      log_file: './logs/health-server-combined.log',
      time: true
    }
  ]
};
