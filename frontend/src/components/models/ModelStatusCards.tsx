import InfoCard from "@/components/models/InfoCard"

import type { ModelDetails } from "@/types/model"


interface ModelStatusCardsProps {
  model: ModelDetails
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


function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "Unknown"
  }

  return value.toLocaleString()
}


export default function ModelStatusCards({
  model,
}: ModelStatusCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">

      <InfoCard
        title="Release Date"
        value={
          model.createdAt
            ? formatDate(model.createdAt)
            : "Unknown"
        }
      />

      <InfoCard
        title="Likes"
        value={formatNumber(model.likes)}
      />

      <InfoCard
        title="Downloads"
        value={formatNumber(model.downloads)}
      />

      <InfoCard
        title="Last Modified"
        value={
          model.lastModified
            ? formatDate(model.lastModified)
            : "Unknown"
        }
      />

      <InfoCard
        title="Trend Score"
        value={formatNumber(model.trendingScore)}
      />

      <InfoCard
        title="Local Deployment"
        value={
          model.research?.isLocallyDeployable === null ||
          model.research?.isLocallyDeployable === undefined
            ? "Unknown"
            : model.research.isLocallyDeployable
              ? "Supported"
              : "Not Supported"
        }
      />

    </div>
  )
}