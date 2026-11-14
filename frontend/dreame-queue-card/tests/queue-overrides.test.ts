import { describe, expect, it } from "vitest";

import {
  cycledOverrides,
  overrideLabel,
  resolvedOverrideValue,
} from "../src/queue-overrides";

describe("HA Dreame queue override helpers", () => {
  it("uses sensible fallback values when overrides are missing", () => {
    expect(resolvedOverrideValue("water_volume", {})).toBe(2);
    expect(resolvedOverrideValue("suction_level", {})).toBe(1);
    expect(resolvedOverrideValue("repeats", {})).toBe(1);
  });

  it("returns human labels for resolved values", () => {
    expect(overrideLabel("water_volume", {})).toBe("Med");
    expect(overrideLabel("water_volume", { water_volume: 0 })).toBe("Off");
    expect(overrideLabel("suction_level", { suction_level: -1 })).toBe("Off");
    expect(overrideLabel("repeats", { repeats: 3 })).toBe("x3");
  });

  it("cycles water volume through off, min, med, and max", () => {
    expect(cycledOverrides("water_volume", { water_volume: 0 }).water_volume).toBe(1);
    expect(cycledOverrides("water_volume", { water_volume: 1 }).water_volume).toBe(2);
    expect(cycledOverrides("water_volume", { water_volume: 2 }).water_volume).toBe(3);
    expect(cycledOverrides("water_volume", { water_volume: 3 }).water_volume).toBe(0);
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

  it("cycles suction through off, min, med, max, and turbo", () => {
    expect(cycledOverrides("suction_level", { suction_level: -1 }).suction_level).toBe(0);
    expect(cycledOverrides("suction_level", { suction_level: 0 }).suction_level).toBe(1);
    expect(cycledOverrides("suction_level", { suction_level: 2 }).suction_level).toBe(3);
    expect(cycledOverrides("suction_level", { suction_level: 3 }).suction_level).toBe(-1);
  });

  it("cycles repeats between x1, x2, and x3", () => {
    expect(cycledOverrides("repeats", { repeats: 1 }).repeats).toBe(2);
    expect(cycledOverrides("repeats", { repeats: 2 }).repeats).toBe(3);
    expect(cycledOverrides("repeats", { repeats: 3 }).repeats).toBe(1);
  });

  it("cycles from the displayed fallback when a field is missing", () => {
    expect(overrideLabel("repeats", {})).toBe("x1");
    expect(cycledOverrides("repeats", {}).repeats).toBe(2);
    expect(cycledOverrides("water_volume", {}).water_volume).toBe(3);
    expect(cycledOverrides("suction_level", {}).suction_level).toBe(2);
  });
});
