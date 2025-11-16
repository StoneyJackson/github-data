## [2.1.3](https://github.com/StoneyJackson/github-data/compare/v2.1.2...v2.1.3) (2025-11-16)


### Bug Fixes

* **graphql:** add missing creator field to milestone fragments ([3d71890](https://github.com/StoneyJackson/github-data/commit/3d71890e2a0a40c443f87b651a3887372fc3de68))
* **graphql:** prevent double conversion of milestone objects ([fe6782c](https://github.com/StoneyJackson/github-data/commit/fe6782c8534413bb9db80c74508413c033fa7799))
* **lint:** remove unused import and fix line length violations ([5ff6b3b](https://github.com/StoneyJackson/github-data/commit/5ff6b3bbe81ad857053021ec1b7142c3cbba6ffa))
* **save:** update SaveEntityStrategy to use converter registry ([db0c87c](https://github.com/StoneyJackson/github-data/commit/db0c87cb04366da52d581e82feb1151753ce0739))

## [2.1.2](https://github.com/StoneyJackson/github-data/compare/v2.1.1...v2.1.2) (2025-11-10)


### Bug Fixes

* trigger release ([a864cd2](https://github.com/StoneyJackson/github-data/commit/a864cd2f8b70ee0a4b75bf8e8592f71d02c31eda))

## [2.1.1](https://github.com/StoneyJackson/github-data/compare/v2.1.0...v2.1.1) (2025-11-03)


### Bug Fixes

* resolve 6 critical manual testing errors ([95c3d94](https://github.com/StoneyJackson/github-data/commit/95c3d94db7bc24fb8078344960006dd60c20cc1c))
* resolve additional GraphQL field and node limit errors ([8a191bd](https://github.com/StoneyJackson/github-data/commit/8a191bd84f9e6da1f93bf8ff3f71464dcbdfceec))
* resolve PullRequest validation and remaining node limit errors ([47df6a3](https://github.com/StoneyJackson/github-data/commit/47df6a3b45e0b2d40908f4ccfa8a962e741fbeb5))

# [2.1.0](https://github.com/StoneyJackson/github-data/compare/v2.0.0...v2.1.0) (2025-11-03)


### Features

* **releases:** add comprehensive release and tag save/restore functionality ([#42](https://github.com/StoneyJackson/github-data/issues/42)) ([1a5a669](https://github.com/StoneyJackson/github-data/commit/1a5a669d6399743d8cb81bb398775957545084ac))

# [2.0.0](https://github.com/StoneyJackson/github-data/compare/v1.12.0...v2.0.0) (2025-10-30)


### Bug Fixes

* code quality and type annotation improvements ([2ec434d](https://github.com/StoneyJackson/github-data/commit/2ec434d48370aec2d26219f0033d0dd675acdfef))
* exit with non-zero code when entity operations fail ([787f7d2](https://github.com/StoneyJackson/github-data/commit/787f7d259b9dc73790b03fcdc31c6ac43826eaca))
* remove unused import and sort coverage by Miss ([c0ed5e7](https://github.com/StoneyJackson/github-data/commit/c0ed5e740d5a070faf19b1759b663b5be12451ce))
* remove unused imports from integration tests ([c6bee9e](https://github.com/StoneyJackson/github-data/commit/c6bee9e2acb6fcced7bc0fcc8c9fb1edbc18f1c5))
* resolve linting and type checking errors ([6b58e42](https://github.com/StoneyJackson/github-data/commit/6b58e42a269e6e8c2c5635a961ca9a7f4edd2397))
* update git container tests for entity registry refactoring ([7f267d4](https://github.com/StoneyJackson/github-data/commit/7f267d443ab0fdda6e6334ffe98afe8f96354e2b))
* update tests for generate_entity service requirements ([f59ca3c](https://github.com/StoneyJackson/github-data/commit/f59ca3ccab6d0415499c239c48f1ddd96b6e97a1))
* write error messages to stderr instead of stdout ([f8dfa33](https://github.com/StoneyJackson/github-data/commit/f8dfa337feac0677d5c843b1c8d177ba6d43a9ae))


### Features

* add base protocols for entity system ([fdd3b1c](https://github.com/StoneyJackson/github-data/commit/fdd3b1c19f7433b1afa03c8d65dc0c767411763d))
* add CLI entity generator tool ([ebc8496](https://github.com/StoneyJackson/github-data/commit/ebc8496982ce701f6e7efcfd012cfa22a9de3ff4))
* add EntityRegistry public API methods ([e4f87e5](https://github.com/StoneyJackson/github-data/commit/e4f87e571955bbc81f781df511d626aaf484cca4))
* add EntityRegistry skeleton ([02ed4bf](https://github.com/StoneyJackson/github-data/commit/02ed4bf5f76c7461e040cf5f5f18c1c376b89d3a))
* add factory methods to comments entity ([ea96653](https://github.com/StoneyJackson/github-data/commit/ea96653d84170c7b5a11e47c66d63810a3857ba5))
* add factory methods to EntityConfig protocol ([136b9f1](https://github.com/StoneyJackson/github-data/commit/136b9f19891bf96f844fadaa26c0e6070ee004ba))
* add factory methods to git_repository entity ([8d2f815](https://github.com/StoneyJackson/github-data/commit/8d2f815ccb4166a80e6be392d90e2cfbf8724cf9))
* add factory methods to git_repository entity ([fdb2c9f](https://github.com/StoneyJackson/github-data/commit/fdb2c9fb6e2610eda40706c4a03140e20a9e5ac9))
* add factory methods to issues entity ([c9d1443](https://github.com/StoneyJackson/github-data/commit/c9d1443c45608c2534f4578627c765c7bfe440b3))
* add factory methods to labels entity ([9ae3789](https://github.com/StoneyJackson/github-data/commit/9ae3789e59cea57957602b5259dd1513eee82b86))
* add factory methods to milestones entity ([44ba75e](https://github.com/StoneyJackson/github-data/commit/44ba75eda1b3b0556feb1107f62c67e0e88fb9ff))
* add factory methods to pr_comments entity ([3dd7642](https://github.com/StoneyJackson/github-data/commit/3dd76423509c095e5f55360419c3731ded956cd9))
* add factory methods to pr_review_comments entity ([c300145](https://github.com/StoneyJackson/github-data/commit/c30014521a26913bcf14be6800cadca5824fb849))
* add factory methods to pr_reviews entity ([632b22b](https://github.com/StoneyJackson/github-data/commit/632b22bc8220217c0b1dcc30e8f1b5e90e103da4))
* add factory methods to pull_requests entity ([c3a32ca](https://github.com/StoneyJackson/github-data/commit/c3a32ca58fd53d407c333b28329b3e909cde3cc0))
* add factory methods to sub_issues entity ([e6279bb](https://github.com/StoneyJackson/github-data/commit/e6279bb87f16789cfdf96ac6c318ca1cc384ebc6))
* add RegisteredEntity dataclass ([2815f82](https://github.com/StoneyJackson/github-data/commit/2815f823a49dcfcd2398ff6de19e1dc4a5407ea2))
* add service requirement validation to StrategyFactory ([9d301aa](https://github.com/StoneyJackson/github-data/commit/9d301aa9f2c1d84a256aba5d6eed7a24e123c270))
* add StrategyContext with typed service properties ([ad1af47](https://github.com/StoneyJackson/github-data/commit/ad1af47b790c448e912aaee717b383a6add0b420))
* complete StrategyFactory migration to EntityRegistry ([d439885](https://github.com/StoneyJackson/github-data/commit/d4398855a32f3e72c362dd7d0bf2cb787157ddf8))
* implement dependency validation ([5f14676](https://github.com/StoneyJackson/github-data/commit/5f14676790f6c5c601ac9df1b4706c67b9c2104a))
* implement entity auto-discovery ([b941791](https://github.com/StoneyJackson/github-data/commit/b941791a63979b950d36717bd4ecce8522e7b449))
* implement environment variable loading ([3a72b95](https://github.com/StoneyJackson/github-data/commit/3a72b95f5e26b77aebafca342a6475a2667d07cd))
* implement topological sort for entity execution order ([5c6a151](https://github.com/StoneyJackson/github-data/commit/5c6a1519d8233232c1177149451625dfd022b2b5))
* migrate comments entity with issues dependency ([0d06d27](https://github.com/StoneyJackson/github-data/commit/0d06d272491c9d28f5bea8a2ff970e5a0712e72d))
* migrate git_repository entity to EntityRegistry ([e152759](https://github.com/StoneyJackson/github-data/commit/e152759b56e1960d51fc86f223b2d5ebe5dffe76))
* migrate issues entity with milestone dependency ([537cd18](https://github.com/StoneyJackson/github-data/commit/537cd187aacadd25e4fd5c80cc584638a03f319b))
* migrate labels entity to EntityRegistry ([8e6eaf1](https://github.com/StoneyJackson/github-data/commit/8e6eaf15518cee2415762cc4fec824cdbd92e9f9))
* migrate main entry point to EntityRegistry ([6d029fb](https://github.com/StoneyJackson/github-data/commit/6d029fb411b974299de9c85e0bda757d20248c83))
* migrate milestones entity to EntityRegistry ([33a3fc5](https://github.com/StoneyJackson/github-data/commit/33a3fc59a7b6a1fc14a12199cce8eda9e7f9a475))
* migrate pr_comments entity with pull_requests dependency ([aa8a443](https://github.com/StoneyJackson/github-data/commit/aa8a44358ad6e73947960eb5dc305a499f4b508e))
* migrate pr_review_comments entity with pr_reviews dependency ([095e417](https://github.com/StoneyJackson/github-data/commit/095e417dc5e9e80fc907a7335afaccfd1ce2f5f1))
* migrate pr_reviews entity with pull_requests dependency ([8ae380a](https://github.com/StoneyJackson/github-data/commit/8ae380a5541ad70e5047261149d1419244331573))
* migrate pull_requests entity with milestone dependency ([7221123](https://github.com/StoneyJackson/github-data/commit/7221123060e22d39c2f3677d5fa036ac5dbe48e3))
* migrate RestoreOrchestrator to EntityRegistry ([32f7183](https://github.com/StoneyJackson/github-data/commit/32f7183fd57bae8276f4a2e2fc2c41278f783a48))
* migrate SaveOrchestrator to EntityRegistry ([87cff5d](https://github.com/StoneyJackson/github-data/commit/87cff5de9c64873b35757fee1efd25ecdbc02015))
* migrate sub_issues entity with issues dependency ([3dd8530](https://github.com/StoneyJackson/github-data/commit/3dd85302ef1fc5535b308245d829bd343c0a0f06))
* remove ApplicationConfig class and legacy functions ([1d7c2c5](https://github.com/StoneyJackson/github-data/commit/1d7c2c5e2be8e0ba2859619d2cc152a3e2eeda76))
* update entity generator template with zero-arg factory methods ([6673f89](https://github.com/StoneyJackson/github-data/commit/6673f89debb8026d87bb7e0a1135bc9e206fc237))
* update entity generator templates for StrategyContext pattern ([f7c66e5](https://github.com/StoneyJackson/github-data/commit/f7c66e578dbde8c6cbf87e4718102fcf4f9b6ff3))
* update StrategyFactory to support EntityRegistry ([9ee6f5d](https://github.com/StoneyJackson/github-data/commit/9ee6f5d238e80185215e90a0e4fc8290f193bc96))


### BREAKING CHANGES

* ApplicationConfig class removed. Use EntityRegistry instead.
Legacy save/restore functions removed. Use orchestrators instead.

Signed-off-by: Claude <noreply@anthropic.com>
Signed-off-by: Stoney Jackson <dr.stoney@gmail.com>

# [1.12.0](https://github.com/StoneyJackson/github-data/compare/v1.11.0...v1.12.0) (2025-10-23)


### Features

* implement comprehensive ConfigFactory extensions and testing architecture improvements ([8eb5d77](https://github.com/StoneyJackson/github-data/commit/8eb5d77ed2e6b2e23ac1ae31ba300ba7f4a34b9b))

# [1.11.0](https://github.com/StoneyJackson/github-data/compare/v1.10.0...v1.11.0) (2025-10-23)


### Features

* implement comprehensive GitHubDataBuilder extensions and architecture improvements ([de719fc](https://github.com/StoneyJackson/github-data/commit/de719fcd3eef5dde8b8280b4e404e41c6c4d0cbf))
* implement Phase 1 strategy method naming unification ([39e3973](https://github.com/StoneyJackson/github-data/commit/39e3973db51a11db318dde6ae3b64c48df6cbc71))

# [1.10.0](https://github.com/StoneyJackson/github-data/compare/v1.9.0...v1.10.0) (2025-10-18)


### Features

* **milestones:** complete technical debt paydown with comprehensive quality fixes ([#33](https://github.com/StoneyJackson/github-data/issues/33)) ([b8a175d](https://github.com/StoneyJackson/github-data/commit/b8a175d6bcc000d56596bf4c389342485073373b))

# [1.9.0](https://github.com/StoneyJackson/github-data/compare/v1.8.0...v1.9.0) (2025-10-18)


### Features

* implement comprehensive GitHub milestones support ([#32](https://github.com/StoneyJackson/github-data/issues/32)) ([91e2449](https://github.com/StoneyJackson/github-data/commit/91e244935354ee5f2645ecea15cf3d88f0ceae02))

# [1.8.0](https://github.com/StoneyJackson/github-data/compare/v1.7.0...v1.8.0) (2025-10-16)


### Features

* implement comprehensive PR reviews and comments feature with enhanced testing infrastructure ([715ce66](https://github.com/StoneyJackson/github-data/commit/715ce667afa9a2001ee158b94f27964bec1fbfdb))

# [1.7.0](https://github.com/StoneyJackson/github-data/compare/v1.6.0...v1.7.0) (2025-10-12)


### Features

* selective issue and PR numbers feature ([#28](https://github.com/StoneyJackson/github-data/issues/28)) ([5e3e0ad](https://github.com/StoneyJackson/github-data/commit/5e3e0ad9aab5c7cceb4dbfe2302fc5e3bbe214a3))

# [1.6.0](https://github.com/StoneyJackson/github-data/compare/v1.5.0...v1.6.0) (2025-10-10)


### Features

* enable comprehensive data processing by default ([#26](https://github.com/StoneyJackson/github-data/issues/26)) ([09497cd](https://github.com/StoneyJackson/github-data/commit/09497cdefcc6474a6c91e7f5b9f080d21e0efbb3))

# [1.5.0](https://github.com/StoneyJackson/github-data/compare/v1.4.0...v1.5.0) (2025-10-09)


### Features

* add INCLUDE_ISSUES environment variable for configurable issue save/restore ([#24](https://github.com/StoneyJackson/github-data/issues/24)) ([1cbab1d](https://github.com/StoneyJackson/github-data/commit/1cbab1dc5bc369db12138890f2122b9265a02540))

# [1.4.0](https://github.com/StoneyJackson/github-data/compare/v1.3.0...v1.4.0) (2025-09-30)


### Features

* add INCLUDE_PULL_REQUEST_COMMENTS ([#23](https://github.com/StoneyJackson/github-data/issues/23)) ([7e057fb](https://github.com/StoneyJackson/github-data/commit/7e057fba8e322b7a268a0c9ccfb9c50bea2a9314))

# [1.3.0](https://github.com/StoneyJackson/github-data/compare/v1.2.0...v1.3.0) (2025-09-29)


### Features

* INCLUDE_ISSUE_COMMENTS, INCLUDE_PULL_REQUESTS, and INCLUDE_SUB_ISSUES ([67f1c90](https://github.com/StoneyJackson/github-data/commit/67f1c90711c03066d432e8da82c6a71af6eb369c))

# [1.2.0](https://github.com/StoneyJackson/github-data/compare/v1.1.0...v1.2.0) (2025-09-28)


### Features

* add Claude Code configuration with permission settings ([#21](https://github.com/StoneyJackson/github-data/issues/21)) ([ff353cc](https://github.com/StoneyJackson/github-data/commit/ff353ccafe73f531e2e33f5408dd4707e6ce8334))

# [1.1.0](https://github.com/StoneyJackson/github-data/compare/v1.0.5...v1.1.0) (2025-09-27)


### Features

* flatten Git repository structure from git-data/orgname_reponame to git-repo ([#17](https://github.com/StoneyJackson/github-data/issues/17)) ([27227aa](https://github.com/StoneyJackson/github-data/commit/27227aa19f8b127016dcb63815b143ac8ea3e12f))

## [1.0.5](https://github.com/StoneyJackson/github-data/compare/v1.0.4...v1.0.5) (2025-09-27)


### Bug Fixes

* improve container image cleanup with safe multi-arch support ([#16](https://github.com/StoneyJackson/github-data/issues/16)) ([c711d10](https://github.com/StoneyJackson/github-data/commit/c711d104515a273084db6ded78b053ac17bfbfda))

## [1.0.4](https://github.com/StoneyJackson/github-data/compare/v1.0.3...v1.0.4) (2025-09-26)


### Bug Fixes

* correct GraphQL field name from parentIssue to parent ([#15](https://github.com/StoneyJackson/github-data/issues/15)) ([ae7b0d3](https://github.com/StoneyJackson/github-data/commit/ae7b0d376ecc099bd06ef6e1b5f7e4bc07bf3184))

## [1.0.3](https://github.com/StoneyJackson/github-data/compare/v1.0.2...v1.0.3) (2025-09-26)


### Bug Fixes

* implement client-side position calculation for sub-issues ([#13](https://github.com/StoneyJackson/github-data/issues/13)) ([29ddcf6](https://github.com/StoneyJackson/github-data/commit/29ddcf60bdf64c6ecd18b6ea8e5b190f3110384a))

## [1.0.2](https://github.com/StoneyJackson/github-data/compare/v1.0.1...v1.0.2) (2025-09-26)


### Bug Fixes

* implement multi-tag Docker image strategy for releases ([#11](https://github.com/StoneyJackson/github-data/issues/11)) ([250c4b7](https://github.com/StoneyJackson/github-data/commit/250c4b785eee0d45445630b32d70f0a9f8258522))

## [1.0.1](https://github.com/StoneyJackson/github-data/compare/v1.0.0...v1.0.1) (2025-09-26)


### Bug Fixes

* enhance semantic-release with output capture and release detection ([#8](https://github.com/StoneyJackson/github-data/issues/8)) ([272ae29](https://github.com/StoneyJackson/github-data/commit/272ae29fae768a0a07ee47dbd0c9d82d56614d43))

# 1.0.0 (2025-09-26)


### Bug Fixes

* add missing id fields to GraphQL test data ([ebd49b2](https://github.com/StoneyJackson/github-data/commit/ebd49b24a81abdd03c5cf3ce6f32e3e1e8be3802))
* correct JSON storage test to match module responsibility ([e89c9e0](https://github.com/StoneyJackson/github-data/commit/e89c9e0f2e5d7f34f79bc4d78879d22ee77104f1))
* eliminate pytest warnings and correct session file dates ([42897d7](https://github.com/StoneyJackson/github-data/commit/42897d78582e014799c25b842926d197de2390af))
* remove unused Optional and Callable imports from graphql_client ([9853e93](https://github.com/StoneyJackson/github-data/commit/9853e9376662026f80a6f18543e7dd318be18efd))
* resolve all container integration test failures ([b299be5](https://github.com/StoneyJackson/github-data/commit/b299be52d0dc26a8187f1b518a004f9409477741))
* resolve all mypy type errors and improve type safety ([6ba3c9f](https://github.com/StoneyJackson/github-data/commit/6ba3c9f724e9b8b75ed8bc10277afc84708cdb96))
* resolve style issues and improve container test infrastructure ([5d46345](https://github.com/StoneyJackson/github-data/commit/5d46345254a2dc3175436d92dc23094bcbe6454e))
* resolve test failures in make check command ([f186c37](https://github.com/StoneyJackson/github-data/commit/f186c3798c965377cca9e7310bebcd6ace15c213))
* resolve test warnings and improve container integration testing ([a0ec07f](https://github.com/StoneyJackson/github-data/commit/a0ec07fe952596cd3de178e0eb4aee15f351db33))


### Features

* add Claude Code configuration and migrate documentation ([7695164](https://github.com/StoneyJackson/github-data/commit/7695164dede2378856e4682228e025a8102a24aa))
* add comprehensive Git repository backup and restore functionality ([7d8a48c](https://github.com/StoneyJackson/github-data/commit/7d8a48c60fd139835c14568cddc5f5c4a4347bd5))
* add GitHub workflows and dependency management configuration ([#1](https://github.com/StoneyJackson/github-data/issues/1)) ([cac0e91](https://github.com/StoneyJackson/github-data/commit/cac0e912cb21d05a9274933f0bcef37b509ce38c))
* enhance GitHub API with comprehensive data modeling and manual testing ([04dc4bd](https://github.com/StoneyJackson/github-data/commit/04dc4bd5be3bb7846f10b3595d18e424120b7842))
* enhance test framework with advanced boundary mocks and workflow fixtures ([dd442b3](https://github.com/StoneyJackson/github-data/commit/dd442b30b3ba05dd56db943ed6b432b73ccaa60b))
* enhance test framework with comprehensive marker system and advanced workflows ([44508cc](https://github.com/StoneyJackson/github-data/commit/44508ccfa04b827bc4a884d71f05ee361d265917))
* implement chronological comment ordering with regression test ([3380153](https://github.com/StoneyJackson/github-data/commit/3380153b64a45d6dcc3d9c60be942b7602294882))
* implement closed issue restoration with state and metadata preservation ([0a328ea](https://github.com/StoneyJackson/github-data/commit/0a328eafec2f2b4f8a98b0efb6ef83593fc44b8a))
* implement complete GitHub data backup/restore infrastructure ([0ed34a2](https://github.com/StoneyJackson/github-data/commit/0ed34a278f581c809412a4bde8017e042b231bdd))
* implement comprehensive Clean Code refactoring with GitHub API rate limiting ([189ebe0](https://github.com/StoneyJackson/github-data/commit/189ebe02b6b600905161dbb1d200cec1f0b6ed19))
* implement comprehensive container integration testing framework ([983dea9](https://github.com/StoneyJackson/github-data/commit/983dea9ec99c36d7630bf8059283140e445922d2))
* implement comprehensive pull request backup and restore support ([6837f8e](https://github.com/StoneyJackson/github-data/commit/6837f8ed95bf942ec14c6148bef97e7353369fdf))
* implement comprehensive sub-issues support with hierarchical relationships ([b4e471b](https://github.com/StoneyJackson/github-data/commit/b4e471be2da706bddd6c15d9694616ff2f36c38f))
* implement hybrid GraphQL/REST architecture for GitHub API ([07a5ef3](https://github.com/StoneyJackson/github-data/commit/07a5ef33f3a646d6b750b43ca412a4d00d45e985))
* implement issue number mapping for comment restoration ([b26010a](https://github.com/StoneyJackson/github-data/commit/b26010a1373d57b6cd23f301c8fc6e006105a264))
* implement label conflict resolution strategies ([0113eaa](https://github.com/StoneyJackson/github-data/commit/0113eaa9e043dbe202acf71f9501e72481ecc28a))
* implement original metadata preservation for restored issues and comments ([6458655](https://github.com/StoneyJackson/github-data/commit/64586555cdc5c2ea21b224fff46a6755e63e4133))
* implement pull request filtering during save operations ([cee4d0c](https://github.com/StoneyJackson/github-data/commit/cee4d0c6f0fe04da8565463852f5c6da3c69ba39))

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial DevContainer configuration with Ubuntu base image
- Docker-in-Docker support for containerized development
- Pre-installed development tools (Node.js LTS, Python 3, Git, build tools)
- Claude Code CLI pre-installed
- REUSE wrapper script for license compliance checking
- MIT license with REUSE.toml configuration
- CLAUDE.md file with repository guidance
- Developer scripts directory structure
- README.md file with template structure
- CODE_OF_CONDUCT.md file based on Contributor Covenant 2.1
- CONTRIBUTING.md file with template
- Addopt Conventional Commit messages

### Changed

### Deprecated

### Removed

### Fixed

### Security
