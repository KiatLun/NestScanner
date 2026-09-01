import {
  Card,
  CardContent,
} from "@/components/ui/card"


interface InfoCardProps {
  title: string
  value: string
}


export default function InfoCard({
  title,
  value,
}: InfoCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">

        <p className="text-sm text-muted-foreground">
          {title}
        </p>

        <p className="mt-2 text-lg font-semibold">
          {value}
        </p>

      </CardContent>
    </Card>
  )
}