# Dreame Behavior Knowledge

## Purpose

This document captures observed Dreame robot behavior that should shape queue orchestration,
state reconciliation, and regression tests in `ha_dreame`.

It is public-safe by design. Use generic entity examples and avoid private room names, hostnames,
paths, tokens, and installation-specific assumptions.

## Documentation Rule

Update this document whenever runtime debugging reveals durable behavior that should influence the
integration. Each new entry should include:

- confidence: `Observed`, `Inferred`, or `Unknown`
- the relevant generic signals
- the controller implication
- follow-up tests or implementation tasks

Confirmed regressions should become automated tests in the same or next focused slice.

## Confidence Legend

- `Observed`: verified from runtime logs, state history, or repeatable manual testing.
- `Inferred`: likely from observed behavior or code, but not fully proven.
- `Unknown`: needs a planned experiment before it can drive controller behavior.

## Canonical Signals

Use these signals first when debugging or designing reconciliation logic. Entity ids below are
examples only.

| Signal | Meaning | Notes |
|---|---|---|
| `vacuum.<robot>` state | High-level robot state such as `cleaning`, `returning`, `paused`, or `error` | Useful but too coarse for dock and wash nuance |
| `sensor.<robot>_state` | Detailed robot phase such as washing, sweeping, drying, or paused wash states | Better for dock-prep and wash state machines |
| `sensor.<robot>_task_status` | Task lifecycle such as room cleaning or completed | Can be stale briefly after dispatch |
| `sensor.<robot>_current_room` | Robot-reported current room | Context signal, not strict proof of intended target room |
| `sensor.<robot>_error` | Robot error or maintenance code | Some error states are recoverable operator states |
| `sensor.<robot>_self_wash_base_status` | Dock wash state such as idle, washing, or paused | Important for low-water and dock-prep recovery |
| `sensor.<robot>_clean_water_tank_status` | Clean-water tank presence | Useful to detect refill completion |
| `sensor.<robot>_cleaning_progress` | Job progress percentage | Secondary signal; not sufficient by itself |
| `sensor.<robot>_cleaned_area` | Cleaned area in the current job | May help explain wash decisions |
| `number.<robot>_self_clean_area` | Configured area between wash cycles | May affect when the robot returns to wash |

## Observed Behavior Rules

### Stale Completion Status After Dispatch

- Confidence: `Observed`
- Behavior: `task_status=completed` can remain visible immediately after dispatch.
- Controller implication: do not complete a queue item until a non-completed task status has been
  seen after dispatch.
- Test implication: cover stale-completed-at-dispatch as a non-completion state.

### Post-Run Completion Can Be Missed Without An In-Run Reconcile Tick

- Confidence: `Observed`
- Behavior: during a command-gated alpha smoke test with automatic reconciliation disabled, a room
  can finish successfully and the robot can return to a dock/prep state while the HA Dreame runtime
  still has `task_status_cleared_since_dispatch=false`. A later reconcile evaluation then sees
  `task_status=completed` but ignores it as potentially stale, leaving the standalone queue in
  `running` even though the robot is done.
- Controller implication: command-smoke runbooks need either an in-run reconcile tick or an explicit
  safe post-run completion path. Automatic reconciliation should react to a task-status state
  change instead of relying only on its polling interval. It must still avoid accepting stale
  `task_status=completed` immediately after dispatch and must serialize event and interval passes.
- Test implication: cover post-run `completed` plus dock/prep state after a successful room run when
  no earlier reconcile tick set `task_status_cleared_since_dispatch`. Cover a brief valid completion
  pulse between interval ticks and simultaneous event/interval reconciliation.

### Transient Runtime Unavailability Is Inconclusive

- Confidence: `Observed`
- Behavior: a cloud-backed Dreame update can temporarily make the vacuum and companion entities
  unavailable during an otherwise successful room run.
- Controller implication: missing, `unknown`, or `unavailable` vacuum state must hold the current
  queue item without redispatching, consuming retry budget, or marking the queue `out_of_sync`.
  Once the expected active room is confirmed again, clear retry attempts left by the transient
  outage. A valid cleared-since-dispatch `task_status=completed` remains authoritative even if the
  high-level vacuum state is unavailable.
- Test implication: cover unavailable observations at an exhausted retry count, completion during
  vacuum unavailability, active-room recovery resetting retries, and wrong-room activity preserving
  its retry history.

### Auto-Emptying Is Post-Run Maintenance

- Confidence: `Observed`
- Behavior: after room cleaning, the detailed robot state can report `auto_emptying` while the
  high-level vacuum is docked and task completion is still settling.
- Controller implication: treat auto-emptying as post-run maintenance that waits for task lifecycle
  completion. Do not classify it as resumable dock preparation, retry the room, or send
  `vacuum.start`, even when stale pause attributes are present. Persist that post-run hold only
  after the current queue room has been positively confirmed active; auto-emptying left over from a
  preceding room must not become sticky for the newly dispatched item.
- Test implication: cover auto-emptying as a separate post-run observation and verify that it cannot
  produce resume, redispatch, or terminal queue decisions. Also cover completion dispatch while the
  preceding room still reports auto-emptying.

### Recoverable Robot Errors

- Confidence: `Observed`
- Behavior: some robot error states indicate user-action recovery, such as tank or maintenance
  handling, rather than terminal queue failure.
- Controller implication: preserve the queue run and avoid consuming retry budget until recovery is
  impossible or explicitly timed out.
- Test implication: cover recoverable errors as hold states, not immediate `out_of_sync`.

### Interrupted Room Runs Can Resume After User Action

- Confidence: `Observed`
- Behavior: during an active room run, Dreame can enter a paused or error state such as
  `vacuum_state=paused`, `vacuum_state=error`, `task_status=room_cleaning_paused`, or a recoverable
  `sensor.<robot>_error` value. After the operator fixes the physical issue and presses Continue in
  Dreame, the same room run can resume, progress can continue, and `task_status=completed` can later
  finish the HA Dreame queue item correctly.
- Controller implication: paused/error states during an active room queue should be shown as
  operator-action interruptions, not as ordinary running and not as automatic retry conditions. A
  command-gated Continue control can map to Home Assistant `vacuum.start`; an End control can use the
  existing queue cancel path.
- Test implication: cover interrupted room runs as wait states, cover command-gated manual resume,
  and cover UI controls for Continue/End during interrupted active runs.

### Dock Wash Pause Can Hide Behind High-Level Cleaning State

- Confidence: `Observed`
- Behavior: the high-level vacuum state can still report active cleaning while dock wash is paused.
- Behavior: the detailed `washing_paused` and wash-base `paused` states can be a sub-second pulse.
  After that pulse, the detailed states can return to `washing` while the vacuum attributes continue
  to report `paused=true`, `running=false`, and an active wash phase.
- Controller implication: include detailed robot state and self-wash-base status in reconciliation.
  Use the durable vacuum pause attributes as fallback evidence when the detailed pause pulse falls
  between reconciliation ticks.
  Resume attempts should wait until blocking refill or tank conditions are cleared.
  When resume is requested, call Home Assistant's `vacuum.start` service for the configured vacuum.
- Test implication: cover paused dock wash with high-level `cleaning` as a recoverable hold, including
  refill recovery after the detailed pause signals have already returned to `washing`.

### Current Room Is Noisy During Transitions

- Confidence: `Observed`
- Behavior: `current_room` can report a transit/base/adjacent room during dispatch, dock prep, or
  traversal before the robot reaches the intended room.
- Controller implication: do not treat early room mismatch as proof of wrong-room cleaning without
  supporting progress and activity context.
- Test implication: cover early mismatch at zero or unavailable progress as non-fatal.

### Low Positive Progress Can Still Be Transition Noise

- Confidence: `Observed`
- Behavior: low non-zero progress can appear while `current_room` still reports a different room,
  then self-correct.
- Controller implication: use a sustained mismatch and a meaningful progress threshold before
  issuing stop and redispatch.
- Test implication: cover low-progress mismatch as wait/reconcile, not immediate retry.

### Late Room Flips Near Completion

- Confidence: `Observed`
- Behavior: `current_room` can flip near completion even while the robot is finishing the intended
  work.
- Controller implication: suppress room-mismatch redispatch near completion to avoid restarting an
  almost finished room.
- Test implication: cover high-progress mismatch as non-redispatch behavior.

### Progress Is Job-Level And Secondary

- Confidence: `Observed`
- Behavior: progress can be job-level rather than room-level, and may jump or reset between phases.
- Controller implication: never complete a room from progress alone. Use progress only with task
  status, robot state, error state, and dispatch context.
- Test implication: progress-only completion should be rejected.

### Post-Run Maintenance States Are Not Queue Failures By Default

- Confidence: `Observed`
- Behavior: maintenance prompts can appear after a completed run.
- Controller implication: classify post-run maintenance separately from queue execution failure.
- Test implication: cover post-completion maintenance as completed-with-maintenance, not failed.

### Adding After A Terminal Queue Starts Fresh

- Confidence: `Observed`
- Behavior: after a queue reaches a terminal state such as `completed`, `canceled`, `out_of_sync`,
  or `blocked`, adding a new room is intended to begin a fresh pending queue rather than append to
  stale terminal items.
- Controller implication: reset queue run metadata and stale items before accepting the new pending
  room.
- Test implication: cover add-room behavior after each terminal run state.

### Mop Remove/Install Transitions Are In-Run Maintenance

- Confidence: `Observed`
- Behavior: during a room run, Dreame can report mop maintenance transitions such as
  `task_status=returning_to_remove_mop`, `task_status=returning_to_install_mop`,
  `state=returning_remove_mop`, and `state=returning_install_mop`. The high-level vacuum state can
  briefly become `docked` or report a different current room while the robot is still expected to
  resume and finish the same room flow.
- Controller implication: treat mop remove/install return states as expected in-run maintenance.
  Do not consume normal dispatch retry budget or trigger active-room mismatch redispatch while these
  states are active unless a blocking error is present.
- Test implication: cover mop remove/install transitions as wait states, not `out_of_sync` or retry
  states.

### Runtime Tuning Entities May Become Unavailable During Active Runs

- Confidence: `Observed`
- Behavior: some tuning/select entities can become unavailable while advanced robot modes are active.
- Controller implication: command planning should not assume those entities remain available during
  execution. Apply runtime options before dispatch when possible, and provide fallback behavior.
- Test implication: cover unavailable tuning entity paths before command dispatch logic is added.

### Cleaning Profile Sentinel Values

- Confidence: `Observed`
- Behavior: queue overrides have used sentinel values to represent disabled cleaning branches:
  `water_volume <= 0` means vacuum-only intent, and `suction_level < 0` means mop-only intent.
- Controller implication: profile derivation must resolve a single cleaning mode before dispatch
  and must reject profiles where both vacuuming and mopping are disabled.
- Test implication: cover vacuum-only, mop-only, combined, and invalid disabled-both profiles in
  the pure profile core before command dispatch logic is added.

### Custom Cleaning Is Not Safe As A Generic Dispatch Step

- Confidence: `Observed`
- Behavior: forcing a custom-cleaning profile immediately before room dispatch can fail while the
  robot is active or preparing to run, and it may still not enforce vacuum-only intent reliably.
- Controller implication: ordinary queue dispatch should prefer resolved mode and runtime property
  planning over unconditional custom-cleaning calls. Reserve custom-cleaning commands for explicit
  advanced map overrides once command dispatch is implemented and guarded.
- Test implication: command-planning tests should distinguish ordinary profile derivation from
  explicit advanced custom-cleaning requests.

## Known Pitfalls

1. `task_status` alone is insufficient.
2. `current_room` alone is insufficient.
3. Progress alone is insufficient.
4. Dock and wash states can look stuck while still recoverable.
5. Recoverable operator states should not immediately consume retry budget.
6. Custom-cleaning commands should not be used as an unconditional dispatch prelude.
7. New runtime behavior must default to read-only / command-disabled while old and new controllers run in parallel.
8. Active robot command dispatch must require explicit operator enablement.
9. Mop remove/install transitions can briefly look like dispatch failure but are normal in-run maintenance.
10. A polling interval can miss short task-status transitions; completion handling must be event-aware.
11. Missing cloud-backed robot state is absence of evidence, not evidence that dispatch failed.
12. Auto-emptying is post-run maintenance and must not enter resumable dock-prep logic.

## Experiment Protocol

When running a planned manual test, record:

1. Start and end window.
2. Intended queue or app action.
3. Manual intervention such as pause, refill, stop, or resume.
4. Final outcome.
5. Generic signal timeline for the canonical signals above.
6. Controller implication.
7. Follow-up tests or code tasks.

## Evidence Log Template

```markdown
### YYYY-MM-DD - <test name>
- Confidence:
- Setup:
- Expected:
- Observed timeline:
  - t0:
  - t1:
- Outcome:
- Controller implication:
- Follow-up tests:
```

### 2026-06-27 - Command-Gated Two-Room Queue With Auto Reconcile

- Confidence: `Observed`
- Setup: standalone `ha_dreame` queue with robot commands and automatic reconciliation enabled;
  two rooms queued through the new integration.
- Expected: first room completes, second room dispatches, final queue state is `completed`.
- Observed timeline:
  - t0: queue entered `running`; first room was active and second room was pending.
  - t1: first room progress reached the high nineties and stayed there for several minutes while
    cleaned area and elapsed cleaning time still changed.
  - t2: near first-room completion, `current_room` flipped through other room names/ids and progress
    briefly reset to `0`, then later reported `100` while task status still indicated room cleaning.
  - t3: once `task_status=completed` arrived, the queue marked the first room completed and
    dispatched the second room.
  - t4: after the second room completed, the standalone queue reached `completed`; post-run washing
    left the high-level vacuum state looking active without changing the completed queue state.
- Outcome: successful two-room queue completion with no `out_of_sync` or `blocked` terminal state.
- Controller implication: keep completion gated on task lifecycle rather than progress; tolerate
  late `current_room` flips and post-run dock/wash states after the queue is complete.
- Follow-up tests: add an end-to-end reconcile test covering late room flips plus progress
  `95 -> 0 -> 100` before `task_status=completed`, followed by post-completion washing.

### 2026-07-11 - Low-Water Dock Pause Between Reconcile Ticks

- Confidence: `Observed`
- Setup: one active room queue with robot commands and automatic reconciliation enabled; clean-water
  refill performed after a dock wash stopped for low water.
- Expected: clearing the water condition resumes the same active room automatically.
- Observed timeline:
  - t0: the robot reported a clean-water error during dock preparation.
  - t1: detailed robot and wash-base sensors reported a paused wash for less than one second, then
    returned to `washing`.
  - t2: the error cleared and the clean-water tank reported `installed`.
  - t3: the vacuum entity still reported `paused=true` and `running=false`, but reconciliation saw
    only the non-paused detailed states and issued no resume command.
- Outcome: the queue remained running at zero progress until manual recovery.
- Controller implication: durable vacuum pause attributes must supplement transient detailed pause
  states before refill recovery is evaluated.
- Follow-up tests: cover the full signal transition and verify exactly one recovery start intent is
  produced after the tank becomes ready.

### 2026-07-26 - Transient Cloud Outage Around Room Completion

- Confidence: `Observed`
- Setup: two-room standalone queue with robot commands and automatic reconciliation enabled.
- Expected: the first successful room completes and the second room dispatches.
- Observed timeline:
  - t0: the first room was confirmed active and progressed to completion.
  - t1: multiple brief cloud update timeouts made the vacuum and companion entities unavailable.
  - t2: interval reconciliation treated missing state as dispatch failure and consumed the retry
    budget even though the expected room had been active.
  - t3: the robot docked and entered auto-emptying; `task_status=completed` was visible for roughly
    one second between 20-second reconciliation ticks.
  - t4: the next interval saw a non-completed task value and exhausted retry history, leaving the
    queue `out_of_sync`; the second room was never dispatched.
- Outcome: physical cleaning of the first room succeeded, but orchestration failed because transient
  absence and a missed completion pulse were interpreted as command failure.
- Controller implication: unavailable observations must hold without retries; confirmed matching
  activity must reset old retries; auto-emptying must be a non-resumable post-run hold; task
  completion needs a serialized state-change reconcile path in addition to interval polling.
  Post-run maintenance memory must be scoped to an actively confirmed current queue item so that
  lingering maintenance cannot attach to the next room.
- Follow-up tests: cover outage recovery, a completion pulse between ticks, auto-emptying with stale
  pause attributes, and simultaneous completion-event/interval reconciliation with exactly one next
  room dispatch.

## Open Questions

1. Under what conditions does a multi-room app run return for a mid-job wash?
2. Can cleaned area and progress predict imminent wash return reliably enough to help queue timing?
3. Which detailed state sequence always means it is safe to dispatch the next room?
4. Which error codes are recoverable hold states versus terminal failures?
