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

const FIELD_FALLBACK_VALUE: Record<OverrideField, number> = {
  water_volume: 2,
  suction_level: 1,
  repeats: 1,
};

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

function baseMergedOverrides(
  overrides: OverridesDict | undefined,
  defaults: OverridesDict | undefined,
): OverridesDict {
  const merged: OverridesDict = {};
  for (const [key, value] of Object.entries(defaults ?? {})) {
    if (value !== null && value !== undefined) {
      merged[key] = value;
    }
  }
  for (const [key, value] of Object.entries(overrides ?? {})) {
    if (value !== null && value !== undefined) {
      merged[key] = value;
    }
  }
  return merged;
}

export function optionsForField(field: OverrideField): OverrideOption[] {
  return FIELD_OPTIONS[field].map((option) => ({ ...option }));
}

export function mergedOverrides(
  overrides: OverridesDict | undefined,
  defaults: OverridesDict | undefined,
): OverridesDict {
  return baseMergedOverrides(overrides, defaults);
}

export function resolvedOverrideValue(
  field: OverrideField,
  overrides: OverridesDict | undefined,
  defaults: OverridesDict | undefined,
): number {
  const merged = baseMergedOverrides(overrides, defaults);
  return toIntOrNull(merged[field]) ?? FIELD_FALLBACK_VALUE[field];
}

export function overrideLabel(
  field: OverrideField,
  overrides: OverridesDict | undefined,
  defaults: OverridesDict | undefined,
): string {
  const value = resolvedOverrideValue(field, overrides, defaults);
  const option = FIELD_OPTIONS[field].find((item) => item.value === value);
  return option ? option.label : String(value);
}

export function cycledOverrides(
  field: OverrideField,
  overrides: OverridesDict | undefined,
  defaults: OverridesDict | undefined,
): OverridesDict {
  const merged = baseMergedOverrides(overrides, defaults);
  const options = FIELD_OPTIONS[field];
  const current = toIntOrNull(merged[field]);
  const currentIndex = options.findIndex((option) => option.value === current);
  const nextIndex = currentIndex < 0 ? 0 : (currentIndex + 1) % options.length;
  merged[field] = options[nextIndex].value;
  return merged;
}
