"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MultiSelect } from "@/components/ui/multi-select";
import { Label } from "@/components/ui/label";
import { getLeaderboardLbGet, Qualification } from "@/lib/client";
import { qualToStr } from "@/lib/qualification";
import { useEffect, useState, useMemo } from "react";
import { toast } from "sonner";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

interface LeaderboardEntry {
  number: string;
  status: Qualification;
  organization: string;
  country: string;
  region: string;
  world_rank: number;
  score: number;
  driver: number;
  programming: number;
}

type SortKey = keyof LeaderboardEntry;
type SortDirection = "asc" | "desc" | null;

const GRADE_OPTIONS = ["High School", "Middle School"];

const ALL_COLUMNS: { key: SortKey; label: string }[] = [
  { key: "world_rank", label: "Rank" },
  { key: "number", label: "Team" },
  { key: "organization", label: "Organization" },
  { key: "region", label: "Region" },
  { key: "country", label: "Country" },
  { key: "score", label: "Score" },
  { key: "driver", label: "Driver" },
  { key: "programming", label: "Programming" },
  { key: "status", label: "Status" },
];

const STATUS_OPTIONS = [
  { value: 0 as Qualification, label: "None" },
  { value: 1 as Qualification, label: "Regionals" },
  { value: 2 as Qualification, label: "Worlds" },
];

const COLUMN_OPTIONS = ALL_COLUMNS.map((col) => ({
  value: col.key,
  label: col.label,
}));

// Columns hidden by default
const DEFAULT_HIDDEN_COLUMNS: SortKey[] = ["country", "status"];

// Statuses excluded by default
const DEFAULT_EXCLUDED_STATUSES: Qualification[] = [2];

export default function LeaderBoard() {
  const [data, setData] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(false);

  // Filter state
  const [grade, setGrade] = useState<string>("High School");
  const [region, setRegion] = useState<string>("");
  const [excludedStatuses, setExcludedStatuses] = useState<Qualification[]>(
    DEFAULT_EXCLUDED_STATUSES,
  );

  // Column visibility state - stored as array of hidden column keys
  const [hiddenColumns, setHiddenColumns] = useState<SortKey[]>(
    DEFAULT_HIDDEN_COLUMNS,
  );

  // Sort state
  const [sortKey, setSortKey] = useState<SortKey>("world_rank");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");

  const visibleColumns = useMemo(
    () => ALL_COLUMNS.filter((col) => !hiddenColumns.includes(col.key)),
    [hiddenColumns],
  );

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await getLeaderboardLbGet({
          query: {
            grade,
            region: region || undefined,
            exclude_statuses:
              excludedStatuses.length > 0 ? excludedStatuses : undefined,
            limit: 100,
          },
        });

        if (!res.response.ok) {
          throw new Error(`HTTP error! status: ${res.response.status}`);
        }

        const responseData = res.data as { result: LeaderboardEntry[] };
        setData(responseData.result || []);
      } catch (e) {
        console.error(e);
        throw e;
      } finally {
        setLoading(false);
      }
    };

    toast.promise(fetchData, {
      loading: "Fetching leaderboard data...",
      success: "Leaderboard loaded!",
      error: "Failed to load leaderboard",
      position: "top-center",
    });
  }, [grade, region, excludedStatuses]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      // Cycle through: asc -> desc -> null
      if (sortDirection === "asc") {
        setSortDirection("desc");
      } else if (sortDirection === "desc") {
        setSortDirection(null);
        setSortKey("world_rank"); // Reset to default
      }
    } else {
      setSortKey(key);
      setSortDirection("asc");
    }
  };

  const sortedData = useMemo(() => {
    if (!sortDirection) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];

      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDirection === "asc" ? aVal - bVal : bVal - aVal;
      }

      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      if (sortDirection === "asc") {
        return aStr.localeCompare(bStr);
      }
      return bStr.localeCompare(aStr);
    });
  }, [data, sortKey, sortDirection]);

  const SortIcon = ({ columnKey }: { columnKey: SortKey }) => {
    if (sortKey !== columnKey) {
      return <ArrowUpDown className="ml-1 h-4 w-4 inline opacity-50" />;
    }
    if (sortDirection === "asc") {
      return <ArrowUp className="ml-1 h-4 w-4 inline" />;
    }
    if (sortDirection === "desc") {
      return <ArrowDown className="ml-1 h-4 w-4 inline" />;
    }
    return <ArrowUpDown className="ml-1 h-4 w-4 inline opacity-50" />;
  };

  const hiddenColumnsSet = useMemo(
    () => new Set(hiddenColumns),
    [hiddenColumns],
  );

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-end">
        <div className="flex flex-col gap-2">
          <Label>Grade</Label>
          <Select value={grade} onValueChange={setGrade}>
            <SelectTrigger>
              <SelectValue placeholder="Select grade" />
            </SelectTrigger>
            <SelectContent>
              {GRADE_OPTIONS.map((g) => (
                <SelectItem key={g} value={g}>
                  {g}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-2">
          <Label>Region</Label>
          <input
            type="text"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            placeholder="e.g. Colorado"
            className="border rounded-md px-3 py-2 bg-transparent"
          />
        </div>

        <div className="flex flex-col gap-2">
          <Label>Exclude Teams Qualified For:</Label>
          <MultiSelect
            options={STATUS_OPTIONS}
            selected={excludedStatuses}
            onChange={setExcludedStatuses}
            placeholder="None excluded"
          />
        </div>

        <div className="flex flex-col gap-2">
          <Label>Hide Columns</Label>
          <MultiSelect
            options={COLUMN_OPTIONS}
            selected={hiddenColumns}
            onChange={setHiddenColumns}
            placeholder="None hidden"
          />
        </div>
      </div>

      {/* Table */}
      <div className="w-full overflow-auto rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {visibleColumns.map((col) => (
                <TableHead
                  key={col.key}
                  className="cursor-pointer select-none hover:bg-muted/50"
                  onClick={() => handleSort(col.key)}
                >
                  {col.label}
                  <SortIcon columnKey={col.key} />
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell
                  colSpan={visibleColumns.length}
                  className="text-center py-8"
                >
                  Loading...
                </TableCell>
              </TableRow>
            ) : sortedData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={visibleColumns.length}
                  className="text-center py-8"
                >
                  No teams found
                </TableCell>
              </TableRow>
            ) : (
              sortedData.map((row, idx) => (
                <TableRow key={`${row.number}-${idx}`}>
                  {!hiddenColumnsSet.has("world_rank") && (
                    <TableCell>{row.world_rank}</TableCell>
                  )}
                  {!hiddenColumnsSet.has("number") && (
                    <TableCell className="font-medium">{row.number}</TableCell>
                  )}
                  {!hiddenColumnsSet.has("organization") && (
                    <TableCell className="max-w-72 overflow-clip">
                      {row.organization}
                    </TableCell>
                  )}
                  {!hiddenColumnsSet.has("region") && (
                    <TableCell>{row.region}</TableCell>
                  )}
                  {!hiddenColumnsSet.has("country") && (
                    <TableCell>{row.country}</TableCell>
                  )}
                  {!hiddenColumnsSet.has("score") && (
                    <TableCell>{row.score}</TableCell>
                  )}
                  {!hiddenColumnsSet.has("driver") && (
                    <TableCell>{row.driver}</TableCell>
                  )}
                  {!hiddenColumnsSet.has("programming") && (
                    <TableCell>{row.programming}</TableCell>
                  )}
                  {!hiddenColumnsSet.has("status") && (
                    <TableCell>{qualToStr(row.status)}</TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="text-sm text-muted-foreground">
        Showing {sortedData.length} teams
      </div>
    </div>
  );
}
