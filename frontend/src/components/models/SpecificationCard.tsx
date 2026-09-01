import type { ElementType } from "react"


interface SpecificationCardProps {
  title: string
  value: string
  icon: ElementType
}


export default function SpecificationCard({
  title,
  value,
  icon: Icon,
}: SpecificationCardProps) {
  return (
    <div className="rounded-lg border p-4">

      <div className="mb-3 flex items-center gap-2">

        <Icon className="size-4 text-muted-foreground" />

        <p className="text-sm text-muted-foreground">
          {title}
        </p>

      </div>

      <p className="text-sm font-medium leading-6">
        {value}
      </p>

    </div>
  )
}