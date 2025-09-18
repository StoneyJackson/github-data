What would it take to reorganize src/ as follows.

* Organize by the entities that we save and restore. That way all the code
    related to an entity is co-located.
* Common code is pulled out into frameworks, services, and libraries which
    are put under utils.
* Operations (orchestrators) are placed into their own package.

Goals

* Make it easier to add new entities (e.g., "milestones").
* Bust up large files (e.g., queries files).


```
data/
    issues/
        issue - model
        save/
            job
            graphql/
                queries
                converters
        restore/
            job.py
            restapi/
                queries
                converters
    sub_issues/
        sub_issue - model
        save/
            job
            graphql/
                queries
                converters
        restore/
            job.py
            restapi/
                queries
                converters
    comments/
        ...
    labels/
        ...
operations/
    save    - orchistrator
    restore - orchistrator
utils/
    jobs/
    storage/
    github/
        caching
        rate_limiting
        ...
main
```
