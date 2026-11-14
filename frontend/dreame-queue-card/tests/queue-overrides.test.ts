import { describe, expect, it } from "vitest";

import { cycledOverrides, overrideLabel } from "../src/queue-overrides";

describe("HA Dreame queue override helpers", () => {
  it("labels a field without a stored override as the robot default", () => {
    expect(overrideLabel("water_volume", {})).toBe("Default");
    expect(overrideLabel("suction_level", { suction_level: null })).toBe("Default");
    expect(overrideLabel("repeats", undefined)).toBe("Default");
  });

  it("returns human labels for stored values", () => {
    expect(overrideLabel("water_volume", { water_volume: 2 })).toBe("Med");
    expect(overrideLabel("water_volume", { water_volume: 0 })).toBe("Off");
    expect(overrideLabel("suction_level", { suction_level: -1 })).toBe("Off");
    expect(overrideLabel("repeats", { repeats: 3 })).toBe("x3");
  });

  it("cycles water volume through default, min, med, max, and off", () => {
    expect(cycledOverrides("water_volume", {}).water_volume).toBe(1);
    expect(cycledOverrides("water_volume", { water_volume: 1 }).water_volume).toBe(2);
    expect(cycledOverrides("water_volume", { water_volume: 2 }).water_volume).toBe(3);
    expect(cycledOverrides("water_volume", { water_volume: 3 }).water_volume).toBe(0);
    expect(cycledOverrides("water_volume", { water_volume: 0 })).toEqual({});
  });

  it("cycles a field without dropping unrelated override values", () => {
    const next = cycledOverrides("water_volume", {
      water_volume: 2,
      repeats: 2,
      suction_level: 1,
      cleaning_route: 0,
      custom_mopping_route: null,
    });

    expect(next).toEqual({ water_volume: 3, repeats: 2, suction_level: 1, cleaning_route: 0 });
  });

  it("cycles suction through default, min, med, max, turbo, and off", () => {
    expect(cycledOverrides("suction_level", {}).suction_level).toBe(0);
    expect(cycledOverrides("suction_level", { suction_level: 0 }).suction_level).toBe(1);
    expect(cycledOverrides("suction_level", { suction_level: 2 }).suction_level).toBe(3);
    expect(cycledOverrides("suction_level", { suction_level: 3 }).suction_level).toBe(-1);
    expect(cycledOverrides("suction_level", { suction_level: -1, repeats: 2 })).toEqual({
      repeats: 2,
    });
  });

  it("cycles repeats through default, x1, x2, and x3", () => {
    expect(cycledOverrides("repeats", {}).repeats).toBe(1);
    expect(cycledOverrides("repeats", { repeats: 1 }).repeats).toBe(2);
    expect(cycledOverrides("repeats", { repeats: 2 }).repeats).toBe(3);
    expect(cycledOverrides("repeats", { repeats: 3, water_volume: 1 })).toEqual({
      water_volume: 1,
    });
  });
});
