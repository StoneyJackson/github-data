
---

Reorganize code based on operations as follows:

- Move all code relevant to the save operation under src/operatons/save/
- Move all code relevant to the restore operation under src/operations/restore/
- Move any shared code to src/operations/

---

Save and restore have separate, but very similar, job orchestration frameworks.
Extract a single common framework into src/jobs/

---


```
data/
    issues/
        issue.py - Model
        save/
            job.py
            graphql/
                graphql_queries.py
                graphql_converters.py
        restore/
            job.py
            restapi/
                restapi_queries.py
                restapi_converters.py
    sub_issues/
        sub_issue.py - Model
        save/
            job.py
            graphql/
                queries.py
                converters.py
        restore/
            job.py
            restapi/
                queries
                converters
    comments/
        ...
    labels/
        ...
utils/
    jobs/
    storage/
github/
    caching
    rate_limiting
    ...
main
```
