module.exports = {
  apps: [
    {
      name: 'main-processor',
      script: './src/main.py',
      interpreter: 'python',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault'
      },
      error_file: './logs/main-processor-error.log',
      out_file: './logs/main-processor-out.log',
      log_file: './logs/main-processor-combined.log',
      time: true
    },
    {
      name: 'gmail-watcher',
      script: './src/watchers/file_system_watcher.py',
      interpreter: 'python',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault'
      },
      error_file: './logs/gmail-watcher-error.log',
      out_file: './logs/gmail-watcher-out.log',
      log_file: './logs/gmail-watcher-combined.log',
      time: true
    },
    {
      name: 'whatsapp-watcher',
      script: './src/watchers/whatsapp_watcher.py',
      interpreter: 'python',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault'
      },
      error_file: './logs/whatsapp-watcher-error.log',
      out_file: './logs/whatsapp-watcher-out.log',
      log_file: './logs/whatsapp-watcher-combined.log',
      time: true
    },
    {
      name: 'linkedin-watcher',
      script: './src/watchers/linkedin_watcher.py',
      interpreter: 'python',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault'
      },
      error_file: './logs/linkedin-watcher-error.log',
      out_file: './logs/linkedin-watcher-out.log',
      log_file: './logs/linkedin-watcher-combined.log',
      time: true
    },
    {
      name: 'gold-processor',
      script: './src/main.py',
      interpreter: 'python',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: './src',
        VAULT_PATH: './AI_Employee_Vault',
        GOLD_TIER_ENABLED: 'true'
      },
      error_file: './logs/gold-processor-error.log',
      out_file: './logs/gold-processor-out.log',
      log_file: './logs/gold-processor-combined.log',
      time: true
    }
  ]
};
