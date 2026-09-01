import {
  Cpu,
  Languages,
  Scale,
  SlidersHorizontal,
} from "lucide-react"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import SpecificationCard from "@/components/models/SpecificationCard"

import type { TechnicalProfile } from "@/types/model"


interface TechnicalProfileCardProps {
  profile: TechnicalProfile
}


export default function TechnicalProfileCard({
  profile,
}: TechnicalProfileCardProps) {
  return (
    <Card>

      <CardHeader>

        <CardTitle>
          Technical Profile
        </CardTitle>

        <p className="text-sm text-muted-foreground">
          Technical characteristics and capabilities
          identified during research.
        </p>

      </CardHeader>


      <CardContent className="space-y-8">

        {/* Architecture */}
        <div className="space-y-2">

          <p className="text-sm font-medium">
            Architecture
          </p>

          <p className="max-w-5xl text-sm leading-6 text-muted-foreground">
            {profile.architecture || "Unknown"}
          </p>

        </div>


        {/* Specifications */}
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

          <SpecificationCard
            title="Parameters"
            value={
              profile.parameterCount ||
              "Unknown"
            }
            icon={Cpu}
          />


          <SpecificationCard
            title="Languages"
            value={
              profile.languages?.length
                ? profile.languages.join(", ")
                : "Unknown"
            }
            icon={Languages}
          />


          <SpecificationCard
            title="License"
            value={
              profile.license ||
              "Unknown"
            }
            icon={Scale}
          />

        </div>


        {/* WER */}
        <div className="space-y-2">

          <p className="text-sm font-medium">
            Reported WER
          </p>

          <p className="text-sm leading-6 text-muted-foreground">
            {profile.reportedWer || "Unknown"}
          </p>

        </div>


        {/* Fine tuning */}
        <div className="space-y-2">

          <div className="flex items-center gap-2">

            <SlidersHorizontal className="size-4 text-muted-foreground" />

            <p className="text-sm font-medium">
              Fine-tuning Support
            </p>

          </div>

          <p className="text-sm leading-6 text-muted-foreground">
            {profile.fineTuningSupport || "Unknown"}
          </p>

        </div>

      </CardContent>

    </Card>
  )
}