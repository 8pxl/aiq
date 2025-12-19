import Link from "next/link";
import SignIn from "./components/auth/sign-in";

export default function Home() {
  return (
    <main>
      <Link href="/dev" className="" >
        open dashboard
      </Link>
    </main>
  );
}
