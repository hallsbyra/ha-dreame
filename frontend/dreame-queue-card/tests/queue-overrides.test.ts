import { describe, expect, it } from "vitest";

import {
  cycledOverrides,
  mergedOverrides,
  optionsForField,
  overrideLabel,
  resolvedOverrideValue,
} from "../src/queue-overrides";

describe("HA Dreame queue override helpers", () => {
  const defaults = {
    suction_level: 1,
    water_volume: 2,
    repeats: 1,
    cleaning_route: 0,
  };

  it("merges defaults with item overrides and preserves unrelated dispatch keys", () => {
    expect(
      mergedOverrides(
        {
          water_volume: 3,
        },
        defaults,
      ),
    ).toEqual({
      suction_level: 1,
      water_volume: 3,
      repeats: 1,
      cleaning_route: 0,
    });
  });

  it("uses sensible fallback values when overrides and defaults are missing", () => {
    expect(resolvedOverrideValue("water_volume", {}, {})).toBe(2);
    expect(resolvedOverrideValue("suction_level", {}, {})).toBe(1);
    expect(resolvedOverrideValue("repeats", {}, {})).toBe(1);
  });

  it("returns human labels for resolved values", () => {
    expect(overrideLabel("water_volume", {}, defaults)).toBe("Med");
    expect(overrideLabel("water_volume", { water_volume: 0 }, defaults)).toBe("Off");
    expect(overrideLabel("suction_level", { suction_level: -1 }, defaults)).toBe("Off");
    expect(overrideLabel("repeats", { repeats: 3 }, defaults)).toBe("x3");
  });

  it("exposes stable option lists for rendering controls", () => {
    expect(optionsForField("water_volume").map((option) => option.label)).toEqual([
      "Off",
      "Min",
      "Med",
      "Max",
    ]);
    expect(optionsForField("suction_level").map((option) => option.value)).toEqual([
      -1,
      0,
      1,
      2,
      3,
    ]);
  });

  it("cycles water volume through off, min, med, and max", () => {
    expect(cycledOverrides("water_volume", { water_volume: 0 }, defaults).water_volume).toBe(1);
    expect(cycledOverrides("water_volume", { water_volume: 1 }, defaults).water_volume).toBe(2);
    expect(cycledOverrides("water_volume", { water_volume: 2 }, defaults).water_volume).toBe(3);
    expect(cycledOverrides("water_volume", { water_volume: 3 }, defaults).water_volume).toBe(0);
  });

  it("cycles a field without dropping unrelated override values", () => {
    const next = cycledOverrides(
      "water_volume",
      {
        water_volume: 2,
        repeats: 2,
      },
      defaults,
    );

    expect(next.water_volume).toBe(3);
    expect(next.repeats).toBe(2);
    expect(next.suction_level).toBe(1);
    expect(next.cleaning_route).toBe(0);
  });

  it("cycles suction through off, min, med, max, and turbo", () => {
    expect(cycledOverrides("suction_level", { suction_level: -1 }, defaults).suction_level).toBe(0);
    expect(cycledOverrides("suction_level", { suction_level: 0 }, defaults).suction_level).toBe(1);
    expect(cycledOverrides("suction_level", { suction_level: 2 }, defaults).suction_level).toBe(3);
    expect(cycledOverrides("suction_level", { suction_level: 3 }, defaults).suction_level).toBe(-1);
  });

  it("cycles repeats between x1, x2, and x3", () => {
    expect(cycledOverrides("repeats", { repeats: 1 }, defaults).repeats).toBe(2);
    expect(cycledOverrides("repeats", { repeats: 2 }, defaults).repeats).toBe(3);
    expect(cycledOverrides("repeats", { repeats: 3 }, defaults).repeats).toBe(1);
  });
});
