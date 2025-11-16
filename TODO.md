
## `feat:`

- [ ] [FEAT][CRIT] In a restored GitHub repository, I want autolinks for internal resources
        to point to in internal resouces within the restored GitHub repository,
        not the original repository.
- [ ] [FEAT][HIGH] When restoring a repository, disarm autolinks that
        would cause a reverse autolink from an external GitHub resource.
- [ ] [FEAT][MED] Save/restore branch rules.
- [ ] [FEAT][LOW] Print a deep link to token generation when
        'Error: GITHUB_TOKEN environment variable required'
        so I can immediately get a token.
- [ ] [FEAT][LOW] Print status updates
        so I know progress is being made and what's being done.
- [ ] [FEAT][LOW] Allow a URL for GITHUB_REPO.
- [ ] [FEAT][LOW] Save operation should not require GITHUB_TOKEN if the repository is public.

## `docs:`

- [ ] GITHUB_TOKEN options and examples. For example, on 'save' of public
        repository, recommended because authentecated users have a higher rate
        limit than unauthenticated users.
- [ ] Use $(pwd) in examples to make it easier to get started.
