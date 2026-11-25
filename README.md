<h1 align="center">easyfk-skill</h1>

<p align="center">
  <b>AI Skill suite for EasyFK: scaffold projects, explore the framework, write code, reverse-engineer systems</b>
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> · <b>English</b> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a>
</p>

<p align="center">
  <a href="#3-division-of-labour-across-the-four-skills"><img alt="skills" src="https://img.shields.io/badge/skills-4-2ea44f?style=flat-square"></a>
  <a href="#4-installation"><img alt="agents" src="https://img.shields.io/badge/agents-Cursor%20%7C%20Claude%20Code-blue?style=flat-square"></a>
  <a href="https://www.easybuild.pro/easyfk"><img alt="easyfk" src="https://img.shields.io/badge/easyfk-3.2.12%20%7C%203.5.16-orange?style=flat-square"></a>
  <a href="https://github.com/easybuild-jack/easyfk-skill"><img alt="GitHub stars" src="https://img.shields.io/github/stars/easybuild-jack/easyfk-skill?style=flat-square&logo=github"></a>
</p>

<p align="center">
  <a href="https://www.easybuild.pro/easyfk">Website</a> ·
  <a href="https://www.easybuild.pro/docs/reader/dev-env">Docs</a> ·
  <a href="#4-installation">Install</a> ·
  <a href="#5-how-to-use-it">Usage</a>
</p>

---

It tells AI how a project is built, what the framework provides, how code should be written, and how an existing system actually runs inside an EasyFK project. Projects without EasyFK can still use the framework-agnostic conventions in this suite, but with a noticeable drop in capability.

> ## Understand EasyFK before deciding how to use this
>
> This suite is the companion manual for [EasyFK](https://www.easybuild.pro/easyfk). The module coordinates, layering conventions, config prefixes, class names and annotations described here all come from the framework itself — not from generic Spring experience.
>
> - **The project uses EasyFK**: every capability is available. Read the official site first to understand what this architecture is and which modules it has: **<https://www.easybuild.pro/easyfk>**
> - **The project does not use EasyFK**: still usable, but only the framework-agnostic part — minimal working implementations, Alibaba coding guidelines, docs and plans, self-check and review. Anything EasyFK-specific (module selection, `easyfk-` coordinates and private repository, framework class names, annotations and config prefixes, BOM version routing, framework interpretation during reverse analysis) is ignored and not applied.
>
> **To be clear**: without EasyFK the capability drops sharply. The most valuable part of this suite is the framework capability map and the exact class names and configuration per version. Remove that, and what remains is a general coding convention — useful, but any generic coding skill can provide the same.

---

## 1. How it relates to EasyFK

[EasyFK](https://www.easybuild.pro/easyfk) is an enterprise-grade Java foundation with the positioning of "build once, reuse everywhere": 12 core modules, 40+ pluggable components, unified dependency governance. It turns the infrastructure every project has to rebuild (unified response envelope, exceptions, logging, authentication, ORM, cache, MQ, thread pools…) into standardized components that business projects can pull in and start working with.

The companion AI skill is tightly bound to that architecture for three reasons:

| Reason | Explanation |
|---|---|
| **The framework is closed source; capabilities live only inside it** | `com.mcst:*` jars are published only to a private Maven repository. Which modules exist, what the classes are called, how annotations are written, what the config prefixes are — AI cannot infer these from general knowledge, and a wrong guess means code that does not compile |
| **Coding conventions are dictated by the framework's layering** | `Controller → IXxxApi → Service → Repository → Mapper` (together with the multi-stack `ApiServerImpl / ApiScImpl / ApiDubboImpl` implementations) is an EasyFK convention, not how an ordinary Spring project is written |
| **The framework keeps evolving** | Class names, configuration keys and module sets differ between easyfk versions. The skill loads the snapshot matching the BOM version the project actually depends on, so what gets written is what really runs on that version |

So the judgement has two levels:

- **Has `easyfk-` coordinates or `com.mcst` package names** → follow the full rule set of this suite.
- **Does not** → keep only the framework-agnostic conventions: minimal implementation, Alibaba guidelines, logging and comments, docs and plans, self-check and review, project positioning and business-data dependencies in the project description. Anything EasyFK-related — module selection, coordinates and private repository, class names and annotations, config prefixes, version routing — is skipped, and framework idioms are not forced onto an ordinary Spring project. The help it can offer here is limited and degrades noticeably; if you never intended to use EasyFK, a generic coding skill is the better choice.

## 2. What problem it solves

| Without the skill | With the skill |
|---|---|
| AI does not know the framework already ships `Result`, thread pools, cache, locks and business-number generation, so it writes its own or casually pulls in Guava, commons-lang3 and other duplicate capabilities | Check the framework capability map first; if a module exists, write against the class names and configuration in that module's docs, and only fill the gaps yourself |
| Layering is guesswork: Controller injects Service directly, cross-service calls bypass the contract, transactions and uniqueness checks get missed | Write layer by layer: `String` primary key with UUID, `@Transactional`, `@SingleUniqueField`, the full four-piece contract set at once, then self-check |
| After a framework upgrade, AI still uses old class names and config prefixes | Read the project version from the BOM, route to that version's doc snapshot, and write against that version's API |
| Taking over an unmaintained legacy project feels like reading a foreign language | Reverse-engineer two reports from the entry points: a business analysis report and an architecture analysis report, including flowcharts, sequence diagrams and high-availability design |
| The project cannot state what it is or which data it touches, so change impact is left to human memory | The project description opens with its positioning (business project / component project; component projects must name who they serve), and section 5 lists business-data dependencies: which external data it relies on, which it owns, which it exposes, where each comes from, who consumes it, and what breaks if it changes |
| You review your own work: complex changes miss branches or skip contract sync, and problems surface only in production | After complex changes and new features, spin up a separate sub-agent that did not take part in development and have it review the code against the requirements and design, item by item; blocking issues must be fixed before finishing, and task status is written into the plan document for the supervising layer |

## 3. Division of labour across the four skills

The four skills are installed side by side at the same level and reference each other by name. A requirement is usually led by one of them:

| Skill | The question it answers | Typical triggers |
|---|---|---|
| [easyfk-framework-skill](easyfk-framework-skill/SKILL.md) | What the framework **has**: projects and modules, the problem each module solves, which module fits this requirement, which utility classes exist, what the config prefixes are; the **exact signature** of a class (method overloads, constant values, config defaults) | "Which module for sending MQ", "Is there a ready-made object-mapping utility", "Does easyfk support sharding", "What methods does `RRBuilder` have" |
| [easyfk-dev-skill](easyfk-dev-skill/SKILL.md) | How code **should be written**: layering, naming, each layer's implementation, transactions and exceptions, module split and threading model for architecture-class projects, docs, self-check | "Add a cancel endpoint to the order module", "Create a new project on easyfk", "Write a starter" |
| [easyfk-reverse-skill](easyfk-reverse-skill/SKILL.md) | What the system **looks like**: restore the business analysis report, the architecture analysis report and the business-data dependencies (depends on, owns, exposes) from existing code | "Map out the business flows of this legacy project", "Draw me an overall architecture diagram", "Which business data does this project actually depend on" |
| [easyfk-generator-skill](easyfk-generator-skill/SKILL.md) | How a project **gets created**: EasyFK backends with `efg` (check JDK and `efg` installation, download and install if missing, verify; ask which project type and parameters; write `generator.yml`; invoke the CLI; verify the output); EasyBuild Admin admin-panel frontends with `easybuild-admin` (ask for project name, description, target directory, package manager and template version; scaffold with one `npx` command; verify `package.json` and template structure) | "Create an order microservice with easyfk", "Generate the project skeleton", "Add Entity and business code for a new table", "The table changed, refresh the DTOs", "efg won't install / throws errors", "Create an admin frontend with EasyBuild Admin" |

easyfk-dev-skill has a framework-agnostic portion (minimal implementation, Alibaba guidelines, docs and plans, self-check and review). When the project does not use EasyFK, only that portion is available, all framework-related rules are skipped, and capability degrades noticeably — see §1 for how to tell.

Dependencies flow one way: to create a project, run the generator first (generator → framework version); before writing code, check framework capabilities (dev → framework); when reverse-engineering framework calls, also check the framework (reverse → framework). The generator only produces the project and layered code; how that code should be written and changed is still governed by dev. EasyBuild Admin frontends are the exception: dev's Java layering does not apply — follow the template's own `docs/开发文档.md`.

## 4. Installation

Supports Cursor, Claude Code and other AI coding tools that read `SKILL.md`. The four skills must sit as sibling directories at the **first level** of the skills directory; nesting them under an `easyfk-skill/` subdirectory usually means they are not detected.

```bash
git clone --depth 1 https://github.com/easybuild-jack/easyfk-skill.git
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File easyfk-skill/install.ps1 [-Target <skills directory>]
```

```bash
# macOS / Linux
sh easyfk-skill/install.sh [<skills directory>]
```

- The target directory defaults to `~/.cursor/skills` (per-user, global). To install for a single project use `<project>/.cursor/skills`; for Claude Code use `~/.claude/skills`.
- An existing directory with the same name is deleted first and then installed. The pre-rename legacy `easyfk-skill` directory (`name: easyfk-skill`) is removed as well.
- Restart the IDE or open a new session after installing. **To update**: clone again and rerun the install script.

## 5. How to use it

**No need to name a skill manually.** In an EasyFK project, just state your requirement as usual. The AI first recognises it as an EasyFK project from the build file (`easyfk-` coordinates) or the source package name (`com.mcst`), then loads the docs for the BOM version in use.

For non-EasyFK projects it will not apply the framework idioms; it uses only the general conventions (minimal implementation, docs and plans, self-check and review) and tells you up front that capability is reduced. Ordinary Java projects are not pushed into framework conventions such as `IXxxApi` or `easyfk-` coordinates.

A few real-world requests:

| Your request | What happens |
|---|---|
| "Create an order microservice with easyfk, connecting to the local MySQL `order` database" | Check JDK and `efg`; download, install and verify if missing → ask for project type and parameters → write `generator.yml` → invoke `efg` → verify modules and layered code are complete |
| "Create an admin frontend with EasyBuild Admin" | No JDK or `efg` involved: ask for project name, description, target directory and package manager → `npx easybuild-admin@1.2.0 … --json -y` → verify `package.json` and template structure → `corepack yarn install` / `yarn dev` (port 4000, built-in mock) |
| "Add Entity and business code for a new table in an existing project" | Read the existing configuration to confirm coordinates and package names → add to `db-tables` → run `efg -m` then `efg -s`, without overwriting hand-written files |
| "The table changed, please refresh the DTOs" | Confirm the table structure → `efg -d`, touching only DTOs and Params |
| "Add a cancel endpoint to the order module, with status validation and logging" | Check whether the framework already has the capability → generate the full Controller / Api / Service / Repository set by layer → self-check and explain what changed |
| "I'm done with this requirement, please review it" | Spin up a separate sub-agent that did not take part in development; it reviews the code against requirements, design and change list, and reports blocking / suggested items; blocking items are fixed and re-reviewed, and the result plus task status go into the plan document |
| "I need traffic shaping here — MQ or Disruptor?" | Compare `mq-*` and `queue-disruptor` on persistence and reliability, give the selection and config prefixes; do not hand-roll a queue |
| "What methods does `RRBuilder` have?" "What is the default for this config key?" | Consult the API signature reference for that easyfk version (one per module, with overloads, constant values and config defaults); never invent an API from memory |
| "This project must support both Dubbo and Feign calls" | Propose a contract and implementation split for the multi-stack microservice form |
| "Nobody maintains this legacy project any more; help me make sense of it" | Find every entry point (Controller, MQ consumer, XXL-JOB, Aeron, etcd leader election…) → produce a business analysis report + architecture analysis report + business-data dependency list |
| "Upstream changed the contract multiplier for market data — what do we need to change?" | Consult the "consumers" and "change impact" of market data in the business-data dependency list, and point to the affected modules, endpoints and `Class#method` instead of searching the whole repository |
| "Upgrading to a new easyfk release — what has to change?" | Diff the two snapshots, list renamed config keys and changed class names, keep the old form with a note "changed from version X" |

## 6. Framework dependency

easyfk is **not open source**, but it is free to use. The framework jars are not published to Maven Central or other public repositories; they are obtained from the official private Maven repository.

Repository URL, access token, and the concrete Maven / Gradle configuration are documented on the official site: <https://www.easybuild.pro/easyfk>

This step is a prerequisite: without the repository configured, every `com.mcst:*` dependency fails to resolve (artifact not found or 401).

## 7. Directory structure

```
easyfk-skill/
├── README.md                 English (default)
├── README.zh-CN.md           Simplified Chinese
├── README.zh-TW.md           Traditional Chinese
├── README.ja.md              Japanese
├── install.ps1 / install.sh  Install scripts
├── easyfk-framework-skill/   Framework capability map + version snapshots
│   ├── SKILL.md              Module overview, requirement-based selection, utility list, capability boundaries, dependency setup
│   ├── maintenance.md        Maintenance workflow of the suite itself
│   ├── versions/             Doc snapshots stored per easyfk version
│   │   └── <version>/        VERSION.md, manuals.txt, modules/, api/, manuals/
│   └── scripts/              Snapshot sync scripts, API doc generation scripts
├── easyfk-dev-skill/         Development conventions
│   ├── SKILL.md              General rules, layering, naming, self-check
│   └── rules/                12 rule files split by layer and scenario
├── easyfk-reverse-skill/     Reverse-engineer business and architecture from code
│   └── SKILL.md
└── easyfk-generator-skill/   Create EasyFK backends (efg) and EasyBuild Admin frontends (easybuild-admin)
    ├── SKILL.md              Environment checks, parameter questions, generator.yml, CLI invocation, output verification
    └── reference/
        ├── cli使用手册.md      Original efg CLI manual (full parameters, config examples, database types)
        └── 前端脚手架使用手册.md  Original easybuild-admin manual (parameters, JSON contract, error codes)
```

## 8. Related links

- EasyFK architecture overview: <https://www.easybuild.pro/easyfk>
- EasyFK docs (dev environment, quick start): <https://www.easybuild.pro/docs/reader/dev-env>
- This repository: <https://github.com/easybuild-jack/easyfk-skill.git>

## 9. Contributing

Issues and pull requests are welcome: reporting documentation mistakes, adding snapshots for a new easyfk release, or improving the rules.

- Read the suite maintenance workflow in [easyfk-framework-skill/maintenance.md](easyfk-framework-skill/maintenance.md) before changing skill content. Adding or refreshing a doc snapshot for an easyfk version needs that version's framework source, which only the maintainer can do.
- When changing this README, update all four language versions (`README.md`, `README.zh-CN.md`, `README.zh-TW.md`, `README.ja.md`) together and keep sections and table rows aligned.
- Before submitting, run `install.sh` / `install.ps1` locally to confirm the four skills install correctly at the first level of the skills directory.
- Content in either Chinese or English is fine.
