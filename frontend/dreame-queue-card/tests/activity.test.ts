import { describe, expect, it } from "vitest";

import { deriveRunActivity, sensorEntityIdForVacuum } from "../src/activity";

describe("HA Dreame activity helpers", () => {
  it("returns null when the queue is not running", () => {
    expect(
      deriveRunActivity({
        queueRunState: "idle",
        vacuumState: "cleaning",
      }),
    ).toBeNull();
  });

  it("classifies washing states as preparing", () => {
    expect(
      deriveRunActivity({
        queueRunState: "running",
        vacuumState: "cleaning",
        robotState: "washing",
        taskStatus: "room_cleaning",
      }),
    ).toEqual({
      phase: "preparing",
      label: "Washing pads",
    });
  });

  it("classifies returning to wash during room cleaning as preparing", () => {
    expect(
      deriveRunActivity({
        queueRunState: "running",
        vacuumState: "returning",
        robotState: "returning_to_wash",
        taskStatus: "room_cleaning",
      }),
    ).toEqual({
      phase: "preparing",
      label: "Returning to wash",
    });
  });

  it("classifies generic returning during room cleaning as returning", () => {
    expect(
      deriveRunActivity({
        queueRunState: "running",
        vacuumState: "returning",
        robotState: "unknown",
        taskStatus: "room_cleaning",
      }),
    ).toEqual({
      phase: "returning",
      label: "Returning to base",
    });
  });

  it("classifies active room state as cleaning", () => {
    expect(
      deriveRunActivity({
        queueRunState: "running",
        vacuumState: "cleaning",
        robotState: "sweeping_and_mopping",
        taskStatus: "room_cleaning",
      }),
    ).toEqual({
      phase: "cleaning",
      label: "Vacuuming + mopping",
    });
  });

  it("classifies completed task while the queue is still running as finishing", () => {
    expect(
      deriveRunActivity({
        queueRunState: "running",
        vacuumState: "docked",
        taskStatus: "completed",
      }),
    ).toEqual({
      phase: "finishing",
      label: "Finishing step",
    });
  });

  it("includes known error code labels", () => {
    expect(
      deriveRunActivity({
        queueRunState: "running",
        vacuumState: "error",
        errorCode: "dirty_water_tank",
      }),
    ).toEqual({
      phase: "error",
      label: "dirty water tank full",
    });
  });

  it("shows paused reason when paused has an error code", () => {
    expect(
      deriveRunActivity({
        queueRunState: "running",
        vacuumState: "paused",
        robotState: "washing_paused",
        taskStatus: "room_cleaning",
        errorCode: "water_tank_dry",
      }),
    ).toEqual({
      phase: "paused",
      label: "Paused (clean water tank empty)",
    });
  });
});

describe("sensorEntityIdForVacuum", () => {
  it("maps a vacuum entity to corresponding public companion sensor examples", () => {
    expect(sensorEntityIdForVacuum("vacuum.robot", "state")).toBe("sensor.robot_state");
    expect(sensorEntityIdForVacuum("vacuum.robot", "task_status")).toBe(
      "sensor.robot_task_status",
    );
    expect(sensorEntityIdForVacuum("vacuum.robot", "error")).toBe("sensor.robot_error");
  });

  it("returns null for non-vacuum entity ids", () => {
    expect(sensorEntityIdForVacuum("light.kitchen", "state")).toBeNull();
  });
});
