export default function InfoDisplay() {
  return (
    <div className="flex items-center">
      <div className="flex flex-col text-2xl lg:text-4xl p-2 w-full text-right duration-500">
        <div className="whitespace-nowrap mr-[55%]">
          <span className="font-bold">4231</span> teams
        </div>

        <div className="whitespace-nowrap mr-[24%] ">
          <span className="font-bold">132</span> states qualified
        </div>

        <div className="whitespace-nowrap mr-[10%]">
          <span className="font-bold">23</span> worlds qualified
        </div>

        <div className="whitespace-nowrap mr-[17%]">
          <span className="font-bold">20</span>% worlds capacity
        </div>

        <div className="whitespace-nowrap mr-[30%]">
          <span className="font-bold">5</span> sessions
        </div>
      </div>
    </div>
  )
}
