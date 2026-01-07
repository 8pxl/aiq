"use client";

import * as React from "react";
import { CheckIcon, ChevronDownIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

export interface ComboBoxClassNames {
  /** Classes for the trigger button */
  trigger?: string;
  /** Classes for the trigger icon */
  triggerIcon?: string;
  /** Classes for the popover content */
  content?: string;
  /** Classes for the command container */
  command?: string;
  /** Classes for the search input */
  input?: string;
  /** Classes for the command list */
  list?: string;
  /** Classes for the empty state */
  empty?: string;
  /** Classes for the command group */
  group?: string;
  /** Classes for each item */
  item?: string;
  /** Classes for selected item */
  itemSelected?: string;
  /** Classes for the check icon */
  itemCheck?: string;
}

export interface ComboBoxProps {
  arr: Array<string>;
  text: string;
  /** Controlled value */
  value?: string;
  /** Default value for uncontrolled mode */
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  classNames?: ComboBoxClassNames;
}

export function ComboBox({
  arr,
  text,
  value: controlledValue,
  defaultValue = "",
  onValueChange,
  placeholder,
  disabled = false,
  className,
  classNames = {},
}: ComboBoxProps) {
  const [open, setOpen] = React.useState(false);
  const [internalValue, setInternalValue] = React.useState(defaultValue);

  // Support both controlled and uncontrolled modes
  const isControlled = controlledValue !== undefined;
  const value = isControlled ? controlledValue : internalValue;

  const handleSelect = (currentValue: string) => {
    const newValue = currentValue === value ? "" : currentValue;
    if (!isControlled) {
      setInternalValue(newValue);
    }
    onValueChange?.(newValue);
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          role="combobox"
          aria-expanded={open}
          aria-controls="combobox-content"
          disabled={disabled}
          data-slot="combobox-trigger"
          data-state={open ? "open" : "closed"}
          data-placeholder={!value ? "" : undefined}
          className={cn(
            // Match SelectTrigger styling exactly
            "border-input [&_svg:not([class*='text-'])]:text-muted-foreground",
            "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
            "dark:bg-input/30 dark:hover:bg-input/50",
            "flex w-fit items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-2",
            "whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none",
            "disabled:cursor-not-allowed disabled:opacity-50",
            "hover:bg-muted/50",
            "[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
            className,
            classNames.trigger,
          )}
        >
          <span className="truncate">
            {value
              ? arr.find((x) => x === value)
              : (placeholder ?? `Select ${text}...`)}
          </span>
          <ChevronDownIcon
            data-slot="combobox-trigger-icon"
            className={cn("size-4 opacity-50", classNames.triggerIcon)}
          />
        </button>
      </PopoverTrigger>
      <PopoverContent
        id="combobox-content"
        data-slot="combobox-content"
        className={cn("w-50 p-0", classNames.content)}
      >
        <Command
          data-slot="combobox-command"
          className={cn(classNames.command)}
        >
          <CommandInput
            data-slot="combobox-input"
            placeholder={`Search ${text}...`}
            className={cn(classNames.input)}
          />
          <CommandList
            data-slot="combobox-list"
            className={cn(classNames.list)}
          >
            <CommandEmpty
              data-slot="combobox-empty"
              className={cn(classNames.empty)}
            >
              No {text} found.
            </CommandEmpty>
            <CommandGroup
              data-slot="combobox-group"
              className={cn(classNames.group)}
            >
              {arr.map((x) => {
                const isSelected = value === x;
                return (
                  <CommandItem
                    key={x}
                    value={x}
                    onSelect={handleSelect}
                    data-slot="combobox-item"
                    data-selected={isSelected}
                    className={cn(
                      classNames.item,
                      isSelected && classNames.itemSelected,
                    )}
                  >
                    <CheckIcon
                      data-slot="combobox-item-check"
                      className={cn(
                        "mr-2 h-4 w-4",
                        isSelected ? "opacity-100" : "opacity-0",
                        classNames.itemCheck,
                      )}
                    />
                    {x}
                  </CommandItem>
                );
              })}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
