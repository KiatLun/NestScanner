import InfoCard from "@/components/models/InfoCard"

import type { ModelResearch } from "@/types/model"


interface ModelStatusCardsProps {
  research: ModelResearch | null
}


function formatDate(date: string) {
  return new Date(date).toLocaleDateString(
    undefined,
    {
      day: "numeric",
      month: "short",
      year: "numeric",
    }
  )
}


export default function ModelStatusCards({
  research,
}: ModelStatusCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">

      <InfoCard
        title="Release Date"
        value={
          research?.releaseDate
            ? formatDate(research.releaseDate)
            : "Unknown"
        }
      />


      <InfoCard
        title="Recency"
        value={
          research?.isRecent === null ||
          research?.isRecent === undefined
            ? "Unknown"
            : research.isRecent
              ? "Recent"
              : "Not Recent"
        }
      />


      <InfoCard
        title="Local Deployment"
        value={
          research?.isLocallyDeployable === null ||
          research?.isLocallyDeployable === undefined
            ? "Unknown"
            : research.isLocallyDeployable
              ? "Supported"
              : "Not Supported"
        }
      />

    </div>
  )
}