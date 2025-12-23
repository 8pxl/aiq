"use client"
import Link from "next/link"
import Quals, { QualsInput } from "./quals"
import { authClient } from "@/lib/auth-client"
import QualsDisplay from "./quals";
import { useState } from "react";

function Header() {
  async function handleSignOut(e: MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    await authClient.signOut()
    window.location.href = "/";

  }
  return (
    <div className="w-screen flex justify-between font-borel text-xl">
      <Link href="/" className="" onClick={handleSignOut}>
        amiqualled?
      </Link>
    </div>
  )
}
function Welcome() {
  return (
    <div className="mt-15 text-foreground text-3xl">
      Welcome!
    </div>
  )
}
export default function Dashboard() {
  const [refresh, setRefresh] = useState(0)
  return (
    <div className="flex flex-col m-3 h-[calc(100vh-24px)]">
      <Header />
      < Welcome />
      <div className="mt-2.5 grid grid-rows-3 grid-cols-3 border-1 border-white divide-x divide-y divide-white gap-0 overflow-auto">
        <QualsDisplay refresh={refresh} />
        <div></div>
        <div></div>
        <QualsInput refresh={refresh} setRefresh={setRefresh} />
        <div></div>
        <div></div>
      </div>
    </div >
  )
}
