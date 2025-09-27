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
