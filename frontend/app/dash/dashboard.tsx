"use client"
import Link from "next/link"
import Quals, { QualsInput } from "./quals"
import { authClient } from "@/lib/auth-client"
import QualsDisplay from "./quals";
import { useState } from "react";
import { ExtractDisplay } from "./extract";
import InfoDisplay from "./info";

function Header() {
  async function handleSignOut(e: MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    await authClient.signOut()
    window.location.href = "/";

  }
  const {
    data: session,
  } = authClient.useSession();
  var rightContent;
  if (session) {
    rightContent = (
      <Link href="/" className="text-nowrap" onClick={handleSignOut}>
        sign out
      </Link>
    )
  }
  else {
    rightContent = (
      <Link href="/signin" className="text-nowrap">
        sign in
      </Link>
    )
  }
  return (
    <div className="w-full flex flex-row justify-between">
      <Link href="/" className="font-borel text-xl" >
        amiqualled?
      </Link>
      {rightContent}
    </div>
  )
}
function Welcome() {
  return (<div className="mt-10 text-foreground text-3xl">
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
        <ExtractDisplay />
        <InfoDisplay />
        <QualsInput refresh={refresh} setRefresh={setRefresh} />
      </div>
    </div >
  )
}
