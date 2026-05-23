import { describe, expect, it } from "vitest";

import {
  nextRunningOverrideServiceCall,
  runningOverrideEntityId,
  runningOverrideValueFromState,
} from "../src/live-overrides";

describe("HA Dreame live override helpers", () => {
  it("builds companion override entity ids from a vacuum entity for read-only state lookup", () => {
    expect(runningOverrideEntityId("vacuum.robot", "suction_level")).toBe(
      "select.robot_suction_level",
    );
    expect(runningOverrideEntityId("vacuum.robot", "water_volume")).toBe(
      "number.robot_wetness_level",
    );
    expect(runningOverrideEntityId("sensor.robot_status", "suction_level")).toBeNull();
  });

  it("maps companion entity state to queue override values", () => {
    expect(runningOverrideValueFromState("suction_level", "quiet")).toBe(0);
    expect(runningOverrideValueFromState("suction_level", "turbo")).toBe(3);
    expect(runningOverrideValueFromState("water_volume", "8")).toBe(1);
    expect(runningOverrideValueFromState("water_volume", "16")).toBe(2);
    expect(runningOverrideValueFromState("water_volume", "24")).toBe(3);
    expect(runningOverrideValueFromState("water_volume", "unknown_value")).toBeNull();
  });

  it("cycles running overrides through the ha_dreame command gate service", () => {
    expect(nextRunningOverrideServiceCall("entry-1", "suction_level", "quiet")).toEqual({
      domain: "ha_dreame",
      service: "update_running_override",
      data: {
        config_entry_id: "entry-1",
        field: "suction_level",
        value: 1,
      },
    });
    expect(nextRunningOverrideServiceCall("entry-1", "suction_level", "turbo")).toEqual({
      domain: "ha_dreame",
      service: "update_running_override",
      data: {
        config_entry_id: "entry-1",
        field: "suction_level",
        value: 0,
      },
    });
    expect(nextRunningOverrideServiceCall("entry-1", "water_volume", "8")).toEqual({
      domain: "ha_dreame",
      service: "update_running_override",
      data: {
        config_entry_id: "entry-1",
        field: "water_volume",
        value: 2,
      },
    });
    expect(nextRunningOverrideServiceCall("entry-1", "water_volume", "24")).toEqual({
      domain: "ha_dreame",
      service: "update_running_override",
      data: {
        config_entry_id: "entry-1",
        field: "water_volume",
        value: 1,
      },
    });
    expect(nextRunningOverrideServiceCall("entry-1", "water_volume", "unavailable")).toEqual({
      domain: "ha_dreame",
      service: "update_running_override",
      data: {
        config_entry_id: "entry-1",
        field: "water_volume",
        value: 1,
      },
    });
  });
});
