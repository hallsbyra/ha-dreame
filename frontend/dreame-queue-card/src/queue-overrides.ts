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

function definedOverrides(overrides: OverridesDict | undefined): OverridesDict {
  return Object.fromEntries(
    Object.entries(overrides ?? {}).filter(([, value]) => value !== null && value !== undefined),
  );
}

export function resolvedOverrideValue(
  field: OverrideField,
  overrides: OverridesDict | undefined,
): number {
  return toIntOrNull(overrides?.[field]) ?? FIELD_FALLBACK_VALUE[field];
}

export function overrideLabel(field: OverrideField, overrides: OverridesDict | undefined): string {
  const value = resolvedOverrideValue(field, overrides);
  const option = FIELD_OPTIONS[field].find((item) => item.value === value);
  return option ? option.label : String(value);
}

export function cycledOverrides(
  field: OverrideField,
  overrides: OverridesDict | undefined,
): OverridesDict {
  const next = definedOverrides(overrides);
  const options = FIELD_OPTIONS[field];
  const current = resolvedOverrideValue(field, next);
  const currentIndex = options.findIndex((option) => option.value === current);
  const nextIndex = currentIndex < 0 ? 0 : (currentIndex + 1) % options.length;
  next[field] = options[nextIndex].value;
  return next;
}
