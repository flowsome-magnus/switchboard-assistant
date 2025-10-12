# CI/CD Setup Guide

## GitHub Actions Configuration

This project includes a complete CI/CD pipeline using GitHub Actions for automated testing and deployment.

### Workflow Overview

The CI/CD pipeline includes:

1. **Test Job**: Runs on every push and pull request
   - Sets up Python 3.12 environment
   - Installs dependencies using UV
   - Runs test suite with pytest
   - Validates environment variables

2. **Deploy Job**: Runs only on main branch pushes
   - Deploys the agent to LiveKit Cloud
   - Uses LiveKit CLI for deployment
   - Configures environment variables securely

### Required GitHub Secrets

To enable the CI/CD pipeline, add these secrets to your GitHub repository:

#### Go to: Settings → Secrets and variables → Actions

Add the following repository secrets:

```
# LiveKit Configuration
LIVEKIT_URL=https://your-livekit-server.com
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# AI Services
OPENAI_API_KEY=your-openai-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Optional: Twilio (for SMS/messaging)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```

### Setting Up GitHub Secrets

1. **Navigate to your repository**: https://github.com/flowsome-magnus/switchboard-assistant
2. **Go to Settings**: Click the "Settings" tab
3. **Access Secrets**: In the left sidebar, click "Secrets and variables" → "Actions"
4. **Add Secrets**: Click "New repository secret" for each required secret
5. **Name and Value**: Enter the secret name and value, then click "Add secret"

### Local Development Setup

For local development and testing:

1. **Copy environment template**:
   ```bash
   cp env.example .env
   ```

2. **Fill in your credentials** in `.env`:
   ```bash
   # LiveKit
   LIVEKIT_URL=wss://your-livekit-server.com
   LIVEKIT_API_KEY=your-api-key
   LIVEKIT_API_SECRET=your-api-secret
   
   # AI Services
   OPENAI_API_KEY=your-openai-key
   DEEPGRAM_API_KEY=your-deepgram-key
   
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Run tests locally**:
   ```bash
   uv run pytest tests/ -v
   ```

### Deployment Process

The deployment process is fully automated:

1. **Push to main branch**: Triggers the CI/CD pipeline
2. **Tests run**: Validates code quality and functionality
3. **Deployment**: If tests pass, automatically deploys to LiveKit Cloud
4. **Monitoring**: Check the Actions tab for deployment status

### Manual Deployment

If you need to deploy manually:

```bash
# Install LiveKit CLI
curl -sSL https://get.livekit.io | bash
export PATH="$PATH:$HOME/.local/bin"

# Deploy agent
livekit-cli agent deploy \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET \
  --url $LIVEKIT_URL \
  --name switchboard-agent \
  --entrypoint livekit_switchboard_agent.py
```

### Monitoring and Logs

- **GitHub Actions**: Check the "Actions" tab for pipeline status
- **LiveKit Cloud**: Monitor agent status in the LiveKit dashboard
- **Logs**: View agent logs in the LiveKit Cloud interface

### Troubleshooting

#### Common Issues:

1. **Authentication Errors**: Verify all GitHub secrets are correctly set
2. **Deployment Failures**: Check LiveKit API credentials and permissions
3. **Test Failures**: Ensure all environment variables are properly configured
4. **Import Errors**: Verify all dependencies are installed correctly

#### Getting Help:

- Check the [LiveKit Documentation](https://docs.livekit.io/)
- Review the [GitHub Actions Documentation](https://docs.github.com/en/actions)
- Check the project's [Development Guide](DEVELOPMENT.md)

### Security Best Practices

1. **Never commit secrets**: Use GitHub Secrets for sensitive data
2. **Rotate keys regularly**: Update API keys and secrets periodically
3. **Limit permissions**: Use minimal required permissions for deployment
4. **Monitor access**: Regularly review who has access to your repository

### Next Steps

1. Set up the required GitHub secrets
2. Push your first commit to trigger the pipeline
3. Monitor the deployment in the Actions tab
4. Verify the agent is running in LiveKit Cloud
5. Test the deployed agent with a real call

The CI/CD pipeline will now automatically test and deploy your switchboard agent whenever you push changes to the main branch!
