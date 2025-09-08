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
