"use client"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getjwt } from "@/lib/auth-client"
import { useEffect, useState } from "react"

export function QualsInput() {
  return (
    <div className="w-full col-span-2">
      hello
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
        const res = await fetch("http://127.0.0.1:8000/qualifications", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const json = await res.json();
        setData(json);

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
