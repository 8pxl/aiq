import Link from "next/link";
import { Toaster } from "@/components/ui/sonner"
import LeaderBoard from "./leaderboard";

export default function Home() {
  return (
    <>
      <Link href="/dash" className="" >
        open dashboard
      </Link>
      <LeaderBoard />
    </>
  );
}
