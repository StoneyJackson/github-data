# GitHub Token Setup Guide

This guide explains how to create and configure a GitHub Personal Access Token (PAT) for the GitHub Data project.

## Overview

The GitHub Data project requires a GitHub Personal Access Token with specific permissions to access repository data for backup and restore operations.

## Creating a GitHub Personal Access Token

### Step 1: Access GitHub Settings

1. Go to [GitHub.com](https://github.com) and sign in to your account
2. Click on your profile picture in the upper-right corner
3. Select **Settings** from the dropdown menu
4. In the left sidebar, scroll down and click **Developer settings**
5. Click **Personal access tokens** → **Tokens (classic)**

### Step 2: Generate New Token

1. Click **Generate new token** → **Generate new token (classic)**
2. Enter a descriptive note (e.g., "GitHub Data Backup Tool")
3. Set an expiration date (recommended: 90 days or custom based on your needs)

### Step 3: Select Required Permissions

The GitHub Data project requires the following scopes:

#### Required Scopes
- **`repo`** - Full control of private repositories
  - This includes access to repository issues, labels, and comments
  - Required for both reading (backup) and writing (restore) operations
- **`read:user`** - Read access to user profile information
  - Used for API rate limit monitoring and user context

#### Optional but Recommended
- **`read:org`** - Read access to organization membership
  - Useful if working with organization repositories

### Step 4: Generate and Copy Token

1. Click **Generate token**
2. **Important**: Copy the token immediately - it will not be shown again
3. Store the token securely (password manager recommended)

## Configuration Methods

### Method 1: Environment Variable (Recommended)

Set the token as an environment variable:

```bash
export GITHUB_TOKEN=your_token_here
```

For persistent configuration, add to your shell profile:

```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.bashrc
source ~/.bashrc
```

### Method 2: .env File

Create a `.env` file in the project root:

```bash
cp .env.template .env
```

Edit `.env` and replace the placeholder:

```env
GITHUB_TOKEN=your_token_here
GITHUB_REPO=owner/repository
DATA_PATH=/data
```

**Security Note**: Never commit `.env` files to version control. The `.env` file is already in `.gitignore`.

### Method 3: Docker Environment

When using Docker, pass the token as an environment variable:

```bash
docker run -e GITHUB_TOKEN=your_token_here github-data
```

## Verification

### Test Token Validity

You can verify your token works with:

```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

Expected response includes your user information and remaining rate limits.

### Test with GitHub Data

Run a simple operation to verify setup:

```bash
# Test save operation (read-only)
GITHUB_TOKEN=your_token GITHUB_REPO=owner/repo pdm run python -m src.main save

# Check rate limits
GITHUB_TOKEN=your_token pdm run python -c "
from src.github.boundary import GitHubApiBoundary
boundary = GitHubApiBoundary('$GITHUB_TOKEN')
print(f'Rate limit remaining: {boundary.get_rate_limit_status()["remaining"]}')
"
```

## Security Best Practices

### Token Security
- **Never share tokens** in code, logs, or public channels
- **Use minimal required permissions** - avoid unnecessary scopes
- **Set reasonable expiration dates** - rotate tokens regularly
- **Store securely** using password managers or secure environment variables
- **Revoke unused tokens** in GitHub settings

### Environment Security
- Use `.env` files for local development (never commit to git)
- Use secure environment variable injection in CI/CD
- Consider using GitHub App tokens for production environments

### Monitoring
- Monitor token usage in GitHub Settings → Developer settings → Personal access tokens
- Check rate limit consumption with the GitHub Data project's built-in monitoring
- Set up alerts for approaching rate limits

## Troubleshooting

### Common Issues

**Token not working**
- Verify token has correct permissions (repo, read:user)
- Check token hasn't expired
- Ensure no extra spaces when copying/pasting

**Permission denied errors**
- Verify repository exists and token has access
- For private repositories, ensure `repo` scope is enabled
- For organization repositories, check organization token restrictions

**Rate limit errors**
- Check current rate limit status
- Wait for rate limit reset (shown in error messages)
- Consider using GitHub Apps for higher limits in production

### Rate Limit Information

GitHub API rate limits:
- **Authenticated requests**: 5,000 per hour
- **Unauthenticated requests**: 60 per hour
- **Secondary rate limits**: 100 per minute for writes

The GitHub Data project includes automatic rate limiting and exponential backoff to handle these limits gracefully.

## Token Lifecycle Management

### Regular Maintenance
1. **Review permissions** quarterly - remove unnecessary scopes
2. **Rotate tokens** every 90 days or per your security policy
3. **Audit usage** in GitHub's token management interface
4. **Update documentation** when changing token requirements

### Token Rotation
1. Generate new token with same permissions
2. Update environment variables/configuration
3. Test with new token
4. Revoke old token in GitHub settings

## Additional Resources

- [GitHub Personal Access Token Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [GitHub Data Rate Limiting Documentation](./rate-limiting.md)