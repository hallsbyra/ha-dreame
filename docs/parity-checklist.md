# Dreame Queue Parity Checklist

## Scope

This checklist tracks public-safe parity between the previous private Dreame
queue controller and the standalone `ha_dreame` HACS integration.

It is a release gate, not a private implementation dump. Keep it generic: no
private room names, local entity ids, hostnames, paths, tokens, or dashboards.

Use the previous private controller only as historical behavior reference. The
target is now the standalone HACS integration.

## Status Legend

- `Ported`: implemented in `ha_dreame` with automated coverage.
- `Runtime validated`: verified in HAOS/HACS against real Home Assistant state.
- `Deferred`: intentionally not required before the next release gate.
- `Obsolete`: legacy behavior that should not be preserved.

## Queue And State

| Capability | Status | Evidence | Remaining gate |
|---|---|---|---|
| Queue add room | `Ported` | `ha_dreame.add_queue_room`, queue-core/service tests, packaged card add buttons | Runtime observation during continued alpha use |
| Queue start | `Ported` | `ha_dreame.start_queue`, command-gated dispatch tests | Controlled command smoke with one low-risk room |
| Queue cancel | `Ported` | `ha_dreame.cancel_queue`, service/card tests | Controlled command smoke |
| Queue skip current room | `Ported` | `ha_dreame.skip_current_room`, service/card tests | Controlled command smoke |
| Mid-run pending edits | `Ported` | remove, move, clear-pending, and pending override service/card tests | Runtime observation during a real running queue |
| Terminal add starts fresh | `Ported` | queue-core terminal-state add-room regression coverage | Observe after real completed/canceled/out-of-sync alpha runs |
| Queue run states | `Ported` | sensor/card state coverage for idle, running, completed, blocked, out-of-sync, and error guidance | Runtime observation for each state reached naturally |
| Per-room item states | `Ported` | queue snapshots expose pending, running, completed, skipped, and canceled item state | Runtime observation during controlled command smoke |
| Global default cleaning settings | `Deferred` | legacy behavior exists, but public alpha currently focuses on item overrides and runtime entities | Decide before beta whether this is config-entry option scope or card/user-profile scope |
| Map image below queue controls | `Deferred` | not required for safe alpha queue control | Decide before RC whether map belongs in this card or remains a separate dashboard concern |
| Notifications and voice side effects | `Deferred` | legacy convenience behavior, not required for standalone queue safety | Revisit after command parity and cutover planning |

## Services And Command Safety

| Capability | Status | Evidence | Remaining gate |
|---|---|---|---|
| Namespaced services | `Ported` | services live under `ha_dreame` | Continue public API review before beta |
| Command gate disabled by default | `Runtime validated` | alpha.2 HAOS smoke confirmed running override service is registered and blocked while commands are disabled | Keep disabled for read-only observation |
| Explicit operator enablement | `Ported` | config options and service boundary tests require `allow_robot_commands` before dispatch | Controlled command smoke |
| Manual control preflight | `Ported` | `ha_dreame.get_control_readiness` reports command gate, queue state, vacuum availability, companion entities, and available actions without dispatching commands | Use before each controlled command smoke |
| Start dispatch payload planning | `Ported` | pure dispatch-plan tests cover payload shape before runtime execution | Controlled command smoke against real robot |
| Runtime command executor | `Ported` | command-gated executor tests cover disabled gate and service-call failures | Controlled command smoke |
| Running override controls | `Ported` | PR #100 backend service and PR #101 packaged card controls; alpha.2 installed | Visual/runtime validation while an item is actually running |
| Running override command gate | `Runtime validated` | alpha.2 HAOS smoke confirmed disabled gate blocks `update_running_override` | Recheck during controlled command smoke after enabling commands |
| Interrupted run Continue/End controls | `Ported` | HACS card and `resume_queue` service expose command-gated Continue/End for paused/error active runs | Controlled smoke after installing the next alpha |
| No parallel active control | `Ported` | docs and command gate require a deliberate test window | Operator discipline during alpha/beta testing |

## Runtime Reconciliation

| Capability | Status | Evidence | Remaining gate |
|---|---|---|---|
| Read-only observation extraction | `Ported` | HA state extraction tests and `ha_dreame.evaluate_reconcile` response smoke | Observe during real cleaning cycles |
| Stale completion after dispatch | `Ported` | reconciliation tests require non-completed status before completion | Runtime observation |
| Recoverable robot errors | `Ported` | behavior knowledge and reconciliation tests treat recovery as hold state | Runtime observation during refill/tank cases |
| Dock wash pause recovery | `Ported` | companion states plus durable vacuum pause attributes cover transient low-water pause signals | Validate the fixed refill sequence after installing alpha.6 |
| Current-room transition noise | `Ported` | early mismatch and low-progress mismatch tests avoid false redispatch | Runtime observation |
| Late room flips near completion | `Runtime validated` | confirmed high-progress flips remain holds; unconfirmed wrong-room runs become out of sync | Continue runtime observation |
| Cancel/start task isolation | `Ported` | stop-before-return, active-task start gate, bounded mismatch retries, and unconfirmed completion tests | Validate after installing the next alpha |
| Mop remove/install maintenance | `Ported` | regression coverage from observed legacy failure treats these states as wait states | Runtime observation when maintenance transition occurs |
| Manual app takeover | `Deferred` | pure reconciliation can surface out-of-sync drift, but full operator workflow needs runtime proof | Include in beta parity runbook |
| Restart/reload during active run | `Deferred` | runtime data/unload tests exist, but active-run resume after HA restart needs a deliberate scenario | Decide before RC |
| Idempotent side effects | `Deferred` | side-effect notifications are not yet part of public standalone scope | Revisit only if notification/voice features return |

## Dashboard Card

| Capability | Status | Evidence | Remaining gate |
|---|---|---|---|
| HACS packaged card resource | `Runtime validated` | alpha.1 and alpha.2 HAOS smoke confirmed resource serving | Continue cache/reload observation |
| Lovelace editor | `Ported` | editor tests and packaged editor chunk verification | Manual UI check after each release candidate |
| Queue rendering | `Ported` | card tests cover idle, running, completed, out-of-sync, and blocked guidance | Visual check during real alpha use |
| Add/remove/move/clear controls | `Runtime validated` | frontend service-call tests, HAOS card smoke, and primary-path use | Continue observation during normal use |
| Pending override controls | `Ported` | frontend override tests and service tests | Runtime observation |
| Active start/cancel/skip controls | `Ported` | frontend tests and command-gated services | Controlled command smoke |
| Running override visual controls | `Ported` | frontend tests and alpha.2 installed bundle | Visual validation during a real running state |
| Legacy card exact visual style | `Obsolete` | new card is standalone and HACS-scoped | Keep improving usability, not pixel parity |

## Release Gates

| Gate | Status | Evidence | Remaining gate |
|---|---|---|---|
| Read-only HACS alpha install | `Runtime validated` | alpha.2+ installed through HACS, HA restarted, sensor/services/card resource available | Keep observing normal primary-path use |
| Public-safe docs and behavior knowledge | `Ported` | README, alpha plan, behavior knowledge, release checklist, and AGENTS rules | Update after each durable runtime finding |
| Controlled command smoke | `Runtime validated` | command-gated service stack has completed real primary-path runs | Continue normal-use observation |
| Compact parity checklist | `Ported` | this document | Keep current after each runtime slice |
| Beta promotion | `Deferred` | primary-path use is clean, but remaining hardening decisions are open | Plan after cleanup and release-readiness decisions |
| Cutover issue exists | `Runtime validated` | #110 tracks cutover cleanup and rollback retirement | Close after cleanup is merged or explicitly deferred |
