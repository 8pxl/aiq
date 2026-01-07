import Link from "next/link";
import { Toaster } from "@/components/ui/sonner";
import LeaderBoard from "./leaderboard";
import { getRegionsRegionsGet } from "@/lib/client";
import Header from "./header";

export default async function Home() {
  const fetchData = async () => {
    try {
      const res = await getRegionsRegionsGet();
      console.log(res);
      if (!res.response.ok) {
        throw new Error(`HTTP error! status: ${res.response.status}`);
      }
      return res.data;
    } catch (e) {
      console.error(e);
      throw e;
    }
  };
  const regions = (await fetchData()) as Array<string>;
  regions.unshift("All");

  return (
    <div className="m-3">
      <Header />
      <LeaderBoard regions={regions} />
    </div>
  );
}
