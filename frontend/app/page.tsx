import Link from "next/link";
import SignIn from "./components/auth/sign-in";

export default function Home() {
  return (
    <main>
      <Link href="/dash" className="" >
        open dashboard
      </Link>
    </main>
  );
}
