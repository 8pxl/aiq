"use client"
import { authClient, signIn } from "@/lib/auth-client"
import SignIn from "../components/auth/sign-in";
import Dashboard from "./dashboard";

export default function Home() {
  const {
    data: session,
    isPending, //loading state
    error, //error object
    refetch //refetch the session
  } = authClient.useSession();
  if (session) {
    return (
      <>
        <Dashboard />
      </>
    )
  }
  return (
    <SignIn />
  )
}
