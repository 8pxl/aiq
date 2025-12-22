"use client"
import { authClient, signIn } from "@/lib/auth-client"
import SignIn from "../components/auth/sign-in";
import Dashboard from "./dashboard";

export default function Home() {
  const {
    data: session,
  } = authClient.useSession();
  if (session) {
    return (
      <Dashboard />
    )
  }
  return (
    <SignIn />
  )
}
