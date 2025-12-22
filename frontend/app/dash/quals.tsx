"use client"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getjwt } from "@/lib/auth-client"
import { useEffect, useState } from "react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { InlineInput, Input } from "@/components/ui/input"
import { getQualificationsQualificationsGet, GetQualificationsQualificationsGetData } from "@/lib/client"

export function QualsInput() {
  const [team, setTeam] = useState("")
  // const [qualification, setQualification] = 
  return (
    <div className="text-5xl w-full col-span-2 flex flex-col p-2">
      <div className="text-sm text-right">
        manual qualification adjustment
      </div>
      <div className="flex flex-col gap-1 w-full">
        <div>
          <span>change </span>
          <InlineInput placeholder="86868R" className="uppercase text-5xl w-fit max-w-[4em]" />
          <span>'s</span>
        </div>
        <div className="ml-[25%]">
          qualification status to
        </div>
        <div className="ml-[70%]">
          <Select>
            <SelectTrigger className="italic">
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
export default function QualsDisplay() {
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
        setData(res.data);

      } catch (e) {
        console.error(e)
      }
    }
    fetchData()
  }, [])

  console.log(data)
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
