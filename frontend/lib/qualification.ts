import { Qualification } from "@/lib/client";

export const QUALIFICATION_LABELS: Record<Qualification, string> = {
  0: "none",
  1: "regionals",
  2: "worlds",
};

export const qualToStr = (q: Qualification): string => {
  return QUALIFICATION_LABELS[q] ?? "none";
};

export const strToQual = (s: string): Qualification => {
  switch (s) {
    case "regionals":
      return 1;
    case "worlds":
      return 2;
    default:
      return 0;
  }
};
