"use client"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getjwt } from "@/lib/auth-client"
import { SetStateAction, useEffect, useState } from "react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

import { toast } from "sonner"
import { InlineInput, Input } from "@/components/ui/input"
import { getQualificationsQualificationsGet, putQualificationsQualificationsPut, Qualification } from "@/lib/client"
import { useSonner } from "sonner"
import { error } from "console"


const qualToStr = (q: Qualification) => {
  switch (q) {
    case 1:
      return "regionals"
    case 2:
      return "worlds"
    default:
      return "none"
  }
}

interface Qiprops {
  refresh: number;
  setRefresh: React.Dispatch<React.SetStateAction<number>>;
}
export function QualsInput({ refresh, setRefresh }: Qiprops) {
  const [team, setTeam] = useState("")
  const [qualification, setQualification] = useState("")

  const strToQual = (s: string) => {
    switch (s) {
      case "regionals":
        return 1
      case "worlds":
        return 2
      default:
        return 0
    }

  }

  const submitForm = (value: SetStateAction<string>) => {
    setQualification(value)
    if (team === "")
      return
    async function put() {
      const token = await getjwt()
      if (typeof token !== "string") {
        console.error("invalud token!")
        return
      }
      const res = await putQualificationsQualificationsPut({
        query: {
          status: strToQual(value as string),
          team: team
        },
        headers: {
          authorization: `Bearer ${token}`,
        }
      })
      console.log(res)
      switch (res.response.status) {
        case 200:
          setRefresh(refresh + 1)
          break;
        case 400:
          throw new Error(res.error.detail)

      }
    }

    toast.promise(put, {
      loading: 'updating database',
      success: 'updating qualification succesful!',
      error: 'error!',
      position: 'top-center'

    })
  }
  return (
    <div className="text-5xl w-full col-span-2 flex flex-col p-2 bg-background z-20">
      <div className="text-sm text-right">
        manual qualification adjustment
      </div>
      <div className="flex flex-col gap-1 w-full whitespace-nowrap">
        <div>
          <span>change </span>
          <InlineInput
            placeholder="86868R"
            value={team}
            onChange={(e) => setTeam(e.target.value.toUpperCase())}
            className="uppercase text-5xl w-fit max-w-[4em]" />
          <span>'s</span>
        </div>
        <div className=" text-right mr-[19%]">
          qualification status to
        </div>
        <div className="flex flex-row justify-between">
          <span>
          </span>
          <Select
            value={qualification}
            onValueChange={submitForm}
          >
            <SelectTrigger className="italic w-[8.5ch]">
              <SelectValue placeholder="regionals" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="worlds">worlds</SelectItem>
              <SelectItem value="regionals">regionals</SelectItem>
              <SelectItem value="none">none</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  )
}

interface Qdprops {
  refresh: number
}
export default function QualsDisplay({ refresh }: Qdprops) {
  const [data, setData] = useState<Record<string, any>[]>([]);
  useEffect(() => {
    async function fetchData() {
      try {
        const token = await getjwt()
        if (typeof token !== "string") return
        const res = (await getQualificationsQualificationsGet({
          headers: {
            authorization: `Bearer ${token}`,
          }
        }))
        if (!res.response.ok) {
          throw new Error(`HTTP error! status: ${res.response.status}`);
        }
        let data = res.data

        for (const entry of data) {
          entry["status"] = qualToStr(entry["status"])
        }
        setData(data);

      } catch (e) {
        console.error(e)
      }
    }
    toast.promise(fetchData, {
      loading: 'fetching data...',
      success: 'fetching data succesful!',
      error: 'error!',
      position: 'top-center'

    })
    // fetchData()
  }, [refresh])

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
                <TableCell key={col}>
                  {row[col]?.toString() ?? ""}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
