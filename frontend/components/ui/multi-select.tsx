"use client";

import * as React from "react";
import { CheckIcon, ChevronDownIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface MultiSelectOption<T extends string | number = string> {
  value: T;
  label: string;
}

interface MultiSelectProps<T extends string | number = string> {
  options: MultiSelectOption<T>[];
  selected: T[];
  onChange: (selected: T[]) => void;
  placeholder?: string;
  className?: string;
}

export function MultiSelect<T extends string | number = string>({
  options,
  selected,
  onChange,
  placeholder = "Select items...",
  className,
}: MultiSelectProps<T>) {
  const [open, setOpen] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleOption = (value: T) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  const selectedLabels = options
    .filter((opt) => selected.includes(opt.value))
    .map((opt) => opt.label);

  const displayText =
    selectedLabels.length > 0
      ? selectedLabels.length <= 2
        ? selectedLabels.join(", ")
        : `${selectedLabels.length} selected`
      : placeholder;

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={cn(
          "border-input flex w-full items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-2 shadow-xs transition-colors",
          "hover:bg-muted/50",
          "disabled:cursor-not-allowed disabled:opacity-50",
          open && "ring-2 ring-ring ring-offset-2",
        )}
      >
        <span
          className={cn(
            "truncate text-sm",
            selectedLabels.length === 0 && "text-muted-foreground",
          )}
        >
          {displayText}
        </span>
        <ChevronDownIcon
          className={cn(
            "size-4 shrink-0 opacity-50 transition-transform",
            open && "rotate-180",
          )}
        />
      </button>

      {open && (
        <div
          className={cn(
            "absolute top-full left-0 z-50 mt-1 w-full min-w-[180px] rounded-md border bg-popover p-1 shadow-md",
            "animate-in fade-in-0 zoom-in-95",
          )}
        >
          {options.map((option) => {
            const isSelected = selected.includes(option.value);
            return (
              <div
                key={String(option.value)}
                onClick={() => toggleOption(option.value)}
                className={cn(
                  "relative flex cursor-pointer items-center gap-2 rounded-sm py-1.5 pr-8 pl-2 text-sm",
                  "hover:bg-accent hover:text-accent-foreground",
                  "select-none outline-none",
                  isSelected && "bg-accent/50",
                )}
              >
                <span className="flex-1">{option.label}</span>
                {isSelected && (
                  <span className="absolute right-2 flex size-4 items-center justify-center">
                    <CheckIcon className="size-4" />
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
