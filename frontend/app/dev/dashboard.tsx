import Link from "next/link"
import Quals from "./quals"

function Header() {
  return (
    <div className="w-screen flex justify-between font-borel text-xl">
      <Link href="/" className="">
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
  return (
    <div className="flex flex-col m-3">
      <Header />
      < Welcome />
      <Quals />
    </div>
  )
}
