"use client"
import { Table, TableCaption, TableHeader } from "@/components/ui/table"
import { getjwt } from "@/lib/auth-client"
import { useEffect, useState } from "react"

export default function Quals() {
  const [data, setData] = useState("")
  useEffect(() => {
    async function fetchData() {
      try {
        const token = await getjwt()
        if (typeof token !== "string") return
        const res = await fetch("http://127.0.0.1:8000/teams", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const json = await res.json();
        setData(json);
        console.log(json)

      } catch (e) {
        console.error(e)
      }
    }
    fetchData()
  }, [])

  return (
    <>
      <Table>
        <TableCaption>team qualifications</TableCaption>
      </Table>
    </>
  )
}
