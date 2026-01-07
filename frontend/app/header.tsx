import Link from "next/link";

function Logo() {
  return (
    <div className="w-screen flex justify-between font-borel text-xl">
      <Link href="/" className="">
        amiqualled?
      </Link>
    </div>
  );
}

export default function Header() {
  return (
    <div className="flex flex-row justify-around">
      <Logo />
      <Link href="/dash" className="text-nowrap">
        open dashboard
      </Link>
    </div>
  );
}
