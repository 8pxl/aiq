"use client"
import { authClient, signIn } from "@/lib/auth-client"
import SignIn from "../components/auth/sign-in";
import Dashboard from "./dashboard";

export default function Home() {
  return (
    <Dashboard />
  )
  // }
  // return (
  //   <SignIn />
  // )
}
