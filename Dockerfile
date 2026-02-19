FROM python:3.13-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 + PM2
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g pm2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies (cloud only - no Playwright)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY src/ ./src/
COPY mcp/ ./mcp/
COPY deploy/ ./deploy/
COPY ecosystem.cloud.config.js ./
COPY .env.example ./.env.example

# Create vault directory structure
RUN mkdir -p AI_Employee_Vault/Inbox \
             AI_Employee_Vault/Needs_Action \
             AI_Employee_Vault/Done \
             AI_Employee_Vault/Pending_Approval \
             AI_Employee_Vault/Approved \
             AI_Employee_Vault/Rejected \
             AI_Employee_Vault/Plans \
             AI_Employee_Vault/Logs \
             AI_Employee_Vault/Briefings \
             AI_Employee_Vault/Business/Accounting \
             AI_Employee_Vault/Business/Social \
             logs

# Set permissions for deploy scripts
RUN chmod +x deploy/*.sh

# Environment
ENV PYTHONPATH=/app/src
ENV VAULT_PATH=/app/AI_Employee_Vault
ENV DEPLOYMENT_MODE=cloud
ENV HEALTH_PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Start PM2 with cloud config
CMD ["pm2-runtime", "ecosystem.cloud.config.js"]
