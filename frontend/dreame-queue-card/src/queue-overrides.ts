export type OverrideField = "water_volume" | "suction_level" | "repeats";

export type OverrideOption = {
  value: number;
  label: string;
};

type OverridesDict = Record<string, unknown>;

const FIELD_OPTIONS: Record<OverrideField, OverrideOption[]> = {
  water_volume: [
    { value: 0, label: "Off" },
    { value: 1, label: "Min" },
    { value: 2, label: "Med" },
    { value: 3, label: "Max" },
  ],
  suction_level: [
    { value: -1, label: "Off" },
    { value: 0, label: "Min" },
    { value: 1, label: "Med" },
    { value: 2, label: "Max" },
    { value: 3, label: "Turbo" },
  ],
  repeats: [
    { value: 1, label: "x1" },
    { value: 2, label: "x2" },
    { value: 3, label: "x3" },
  ],
};

// Shown for a field the item does not override: dispatch then leaves the robot's own
// current setting in place.
export const DEFAULT_OVERRIDE_LABEL = "Default";

function toIntOrNull(value: unknown): number | null {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? Math.trunc(value) : null;
  }
  if (typeof value === "string") {
    const parsed = Number(value.trim());
    return Number.isFinite(parsed) ? Math.trunc(parsed) : null;
  }
  return null;
}

function definedOverrides(overrides: OverridesDict | undefined): OverridesDict {
  return Object.fromEntries(
    Object.entries(overrides ?? {}).filter(([, value]) => value !== null && value !== undefined),
  );
}

export function overrideLabel(field: OverrideField, overrides: OverridesDict | undefined): string {
  const value = toIntOrNull(overrides?.[field]);
  if (value === null) {
    return DEFAULT_OVERRIDE_LABEL;
  }
  const option = FIELD_OPTIONS[field].find((item) => item.value === value);
  return option ? option.label : String(value);
}

/** Step a field to its next option; after the last option the field returns to Default. */
export function cycledOverrides(
  field: OverrideField,
  overrides: OverridesDict | undefined,
): OverridesDict {
  const next = definedOverrides(overrides);
  const options = FIELD_OPTIONS[field];
  const current = toIntOrNull(next[field]);
  const currentIndex =
    current === null ? -1 : options.findIndex((option) => option.value === current);
  if (currentIndex < options.length - 1) {
    next[field] = options[currentIndex + 1].value;
  } else {
    delete next[field];
  }
  return next;
}
