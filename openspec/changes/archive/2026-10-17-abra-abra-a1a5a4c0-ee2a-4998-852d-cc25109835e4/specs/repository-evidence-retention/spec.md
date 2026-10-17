# Repository evidence retention

## Purpose

Keep the asset repository lean through auditable retention of useful review evidence while protecting authored content, runtime consumers, references and historical verification integrity.

## ADDED Requirements

### Requirement: Measured cleanup inventory
Before cleanup deletes files, the repository maintenance process SHALL record the inspected revision, tracked path inventory, logical byte totals by directory and extension, largest files, and exact duplicate image hash groups. It SHALL distinguish tracked content from untracked/ignored content and LFS pointers from payload bytes, and report missing payloads or unavailable Git/LFS storage measurements explicitly rather than inventing values.

#### Scenario: Inventory precedes deletion
- **WHEN** implementation starts after human approval of this bounded cleanup plan
- **THEN** a read-only revision-bound inventory is produced before any removal, and unresolved tracking or payload identity excludes affected files from removal

### Requirement: Bounded and auditable removal
The cleanup SHALL remove only tracked historical diagnostic PNGs satisfying the approved root and retention rules. Each selected path SHALL have a recorded hash, byte count, reason, consumer disposition and retained counterpart where consolidation applies. Uncertain files SHALL be preserved. Scope expansion SHALL require a decision and renewed human plan approval before implementation proceeds beyond the approved boundary.

#### Scenario: Candidate is a verified obsolete diagnostic
- **WHEN** a tracked PNG is inside an approved candidate root, is not protected, and meets an approved unreferenced-obsolete or exact-duplicate rule
- **THEN** its exact disposition is recorded before removal and its affected live links are repaired in the same change

#### Scenario: Inventory finds larger opportunities elsewhere
- **WHEN** measurement finds a large authored asset, reference image, archive, or diagnostic outside the approved PNG roots
- **THEN** it remains unchanged and any proposed broader removal returns for renewed approval

### Requirement: Preserve essential content and verification
Cleanup SHALL preserve authored sources and textures, supplied inputs and useful reference originals/provenance, required exports, licenses, current catalog/payload dependencies, useful retained comparison sheets/focals, and images required by immutable receipts or active checks and report workflows. It SHALL NOT rewrite historical acceptance records, weaken freshness or predecessor verification, or add history/network retrieval as a normal build prerequisite to enable pruning.

#### Scenario: An evidence image is a shipping dependency
- **WHEN** a candidate PNG is selected by current native preview metadata or an active hash-binding test, receipt or report
- **THEN** its bytes and path remain intact, and normal catalog packaging and verification remain usable offline

### Requirement: Evidence growth is explicit
Fast repository checks SHALL reject new persistent evidence paths or byte-budget growth within the documented evidence roots unless an explicit retention entry supplies the new bound and justification. Disposable validation captures SHALL remain outside tracked evidence by default. Reference originals and authored texture/runtime resources SHALL NOT be subject to a blanket image ignore rule.

#### Scenario: A new capture run is accidentally retained
- **WHEN** a PNG in a monitored evidence root is absent from the retained-path allowlist or exceeds its recorded byte cap
- **THEN** the fast check fails with its path and corrective guidance, rather than silently accepting growth or deleting it

#### Scenario: Useful new evidence is intentionally promoted
- **WHEN** maintainers explicitly retain a useful comparison with a purpose, source/provenance and byte bound in the retention record
- **THEN** the fast check accepts that declared evidence without weakening existing source/image freshness checks

### Requirement: Honest storage accounting
Cleanup reporting SHALL state measured gross removed bytes, added bytes, net logical tracked-checkout reduction and its baseline denominator. It SHALL separate those figures from Git object history, LFS storage and ignored local caches. Cleanup SHALL NOT rewrite Git history or claim historical blob reclamation from ordinary file deletion.

#### Scenario: No eligible files remain
- **WHEN** all candidate files are protected or uncertain
- **THEN** the report states zero eligible removals and measured net change without inventing savings or broadening scope

#### Scenario: Checkout shrinks but history remains
- **WHEN** approved tracked diagnostic PNGs are deleted normally
- **THEN** the report explains that old revisions retain their blobs and full-history clone/storage savings are not established
