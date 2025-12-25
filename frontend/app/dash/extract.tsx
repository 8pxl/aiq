import { Button } from "@/components/ui/button";

export function ExtractDisplay() {
  return (
    <div className="p-2 row-span-2">
      <div className="absolute text-right text-sm">
        api scraper info & controls
      </div>
      <div className="h-full flex items-center">
        <div className="text-lg whitespace-nowrap lg:text-2xl flex flex-col w-full duration-500">
          <div>
            time since last qualification update:
          </div>
          <div>
            34:00
          </div>
          <Button
            className="w-full"
          >
            trigger update
          </Button>

          <div className="mt-5 mb-5 w-full h-px bg-white">
          </div>
          <div>
            time since last sig update:
          </div>
          <div>
            31:00
          </div>
          <Button
            className="w-full"
          >
            trigger update
          </Button>

          <div className="mt-5 mb-5 w-full h-px bg-white">
          </div>
          <div>
            time since last worlds update:
          </div>
          <div>
            24:00
          </div>
          <Button
            className="w-full"
          >
            trigger update
          </Button>
        </div>
      </div>

    </div>
  )
}
