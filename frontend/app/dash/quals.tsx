"use client";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getjwt } from "@/lib/auth-client";
import { SetStateAction, useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { toast } from "sonner";
import { InlineInput } from "@/components/ui/input";
import {
  getQualificationsQualificationsGet,
  putQualificationsQualificationsPut,
} from "@/lib/client";
import { qualToStr, strToQual } from "@/lib/qualification";

interface Qiprops {
  refresh: number;
  setRefresh: React.Dispatch<React.SetStateAction<number>>;
}
export function QualsInput({ refresh, setRefresh }: Qiprops) {
  const [team, setTeam] = useState("");
  const [qualification, setQualification] = useState("");

  const submitForm = (value: SetStateAction<string>) => {
    setQualification(value);
    if (team === "") return;
    async function put() {
      const token = await getjwt();
      if (typeof token !== "string") {
        console.error("invalud token!");
      }
      const res = await putQualificationsQualificationsPut({
        query: {
          status: strToQual(value as string),
          team: team,
        },
        headers: {
          authorization: `Bearer ${token}`,
        },
      });
      switch (res.response.status) {
        case 200:
          setRefresh(refresh + 1);
          break;
        case 400:
          throw new Error(String(res.error?.detail ?? "Unknown error"));
      }
    }

    toast.promise(put, {
      loading: "updating database",
      success: "updating qualification succesful!",
      error: "error updating qualification! make sure you're logged in",
      position: "top-center",
    });
  };
  return (
    <div className="text-5xl w-full col-span-2 flex flex-col p-2 bg-background z-20">
      <div className="text-sm text-right">manual qualification adjustment</div>
      <div className="flex flex-col gap-1 w-full whitespace-nowrap">
        <div>
          <span>change </span>
          <InlineInput
            placeholder="86868R"
            value={team}
            onChange={(e) => setTeam(e.target.value.toUpperCase())}
            className="uppercase text-5xl w-fit max-w-[4em]"
          />
          <span>&apos;s</span>
        </div>
        <div className=" text-right mr-[19%]">qualification status to</div>
        <div className="flex flex-row justify-between">
          <span></span>
          <Select value={qualification} onValueChange={submitForm}>
            <SelectTrigger className="italic w-[8.5ch]">
              <SelectValue placeholder="regionals" />
            </SelectTrigger>
            <SelectContent className="text-5xl">
              <SelectItem value="worlds">worlds</SelectItem>
              <SelectItem value="regionals">regionals</SelectItem>
              <SelectItem value="none">none</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}

interface Qdprops {
  refresh: number;
}

interface QualificationEntry {
  number: string;
  organization: string;
  status: number;
  [key: string]: string | number;
}

export default function QualsDisplay({ refresh }: Qdprops) {
  const [data, setData] = useState<QualificationEntry[]>([]);
  useEffect(() => {
    async function fetchData() {
      const res = await getQualificationsQualificationsGet({});
      if (!res.response.ok) {
        console.error(`HTTP error! status: ${res.response.status}`)
        throw new Error(`HTTP error! status: ${res.response.status}`);
      }
      const responseData = res.data as QualificationEntry[];

      const transformedData = responseData.map((entry) => ({
        ...entry,
        status: qualToStr(entry.status as 0 | 1 | 2) as unknown as number,
      }));
      setData(transformedData);
    }
    toast.promise(fetchData, {
      loading: "fetching data...",
      success: "fetching data succesful!",
      error: "error fetching data!",
      position: "top-center",
    });
    // fetchData()
  }, [refresh]);

  const columns = data.length > 0 ? Object.keys(data[0]) : [];
  return (
    <div className="overflow-auto row-span-2 col-span-2">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <TableHead key={col} className="">
                {col.replace(/_/g, " ")}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((row, idx) => (
            <TableRow key={idx}>
              {columns.map((col) => (
                <TableCell key={col}>{row[col]?.toString() ?? ""}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
