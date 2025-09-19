# Claude Code

Before you use Claude, know the current legal understanding of AI and Claude's
terms of service. Here is a nice podcast that discusses them and how best
to use Claude.

- <https://terms.law/2024/08/24/who-owns-claudes-outputs-and-how-can-they-be-used/>

Legality around AI generated work is evolving. Based on the article above,
one thing you can do to help make a case that what you produced with AI is
copyrightable is to demonstrate significant creative control. One way to do
this is to log your interactions with AI. To this end, this project makes
it easy to dump a summary of your interactions with Claude to
docs/claude-sessions/YYYY-MM-DD-topic.md . I am not a lawyer, and this is not legal advice,
this is just my best attempt to do the right thing.

For repository-specific guidance and development workflows, see the main [CLAUDE.md](../CLAUDE.md) file.

## Starting a Claude session

```bash
claude
```

## Commit with Claude

Have Claude commit work that you produced with Claude's help. Claude
will add itself as a Co-author making it clear that it had a hand in
producing the contents of the commit.

```claude
commit
```

## Ending a Claude session

Before exiting your Claude session, have it generate a session summary.
If you have reached a good checkpoint, also have it commit the work.
Then exit the session. Altogether...

```claude
Please generate a session summary
commit
/exit
```

The sessions are important to prove that you are using Claude as a tool
and that you have clear creative control. These summaries also help with
project continuity by documenting key decisions, commands learned, and
outcomes from each Claude Code interaction.

## Using Project Agents

This project has been configured with specialized Claude agents to help with common development workflows. These agents are automatically available when using Claude Code in this repository.

### Available Agents

The project includes 3 specialized agents configured in `.claude/agents/` using readable Markdown format:

#### Available Agents

- **github-api-specialist**: Handles GitHub API operations, GraphQL/REST integration, rate limiting, and API client development
- **testing-quality**: Manages testing strategies, code quality enforcement, TDD practices, and development tooling 
- **backup-restore-workflow**: Specializes in GitHub repository backup/restore workflows, data migration, and containerized operations

### How Agents Work

Agents can be explicitly invoked by Claude Code's delegation system or requested directly:
```claude
Use the github-api-specialist agent to optimize these API calls
Use the testing-quality agent to run comprehensive quality checks
Use the backup-restore-workflow agent to design this data migration
```

### Agent Capabilities

Each agent has access to specific tools and deep knowledge of project patterns:

- **github-api-specialist**: 
  - GraphQL/REST API optimization and error handling
  - Rate limiting strategies and caching mechanisms
  - GitHub data modeling and API client development
  - Authentication and API response validation

- **testing-quality**:
  - TDD practices with `make test-fast`, `make test-container`, coverage analysis
  - Code quality enforcement with `make lint`, `make format`, `make type-check`
  - Clean Code principles and Conventional Commits compliance
  - Comprehensive testing strategies (unit, integration, container tests)

- **backup-restore-workflow**:
  - CLI design for backup/restore operations
  - Hierarchical data relationships (sub-issues, comment threads)
  - Containerized workflow management and Docker operations
  - Data integrity validation and conflict resolution

### Agent Configuration

Agents are configured using readable Markdown files with YAML frontmatter in `.claude/agents/`:
- Each agent has clearly defined responsibilities and tool access
- Configuration includes specialized knowledge and best practices
- Agents can be customized by editing their respective `.md` files

The agents are designed to work together and will coordinate when needed for complex tasks involving multiple domains.
