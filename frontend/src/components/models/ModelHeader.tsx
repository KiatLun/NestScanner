import { Link } from "react-router-dom"
import {
  ArrowLeft,
  ExternalLink,
} from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { buttonVariants } from "@/components/ui/button"

import type { ModelDetails } from "@/types/model"


interface ModelHeaderProps {
  model: ModelDetails
}


export default function ModelHeader({
  model,
}: ModelHeaderProps) {
  return (
    <div className="space-y-6">

        <Link
        to="/"
        className={buttonVariants({
            variant: "ghost",
            className: "gap-2",
        })}
        >
        <ArrowLeft className="size-4" />
        Back to models
        </Link>


        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-start">

            <div className="space-y-3">

            <div className="flex flex-wrap items-center gap-3">

                <h1 className="text-3xl font-bold tracking-tight">
                {model.name}
                </h1>

                <Badge variant="outline">
                {model.candidateType}
                </Badge>

            </div>


            <p className="text-muted-foreground">
                {model.organisation}
            </p>


            <p className="text-xs text-muted-foreground">
                Model ID: {model.modelId}
            </p>

            </div>

            <a
            href={model.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={buttonVariants({
                variant: "default",
                className: "gap-2",
            })}
            >
            View Model
            <ExternalLink className="size-4" />
            </a>

        </div>

    </div>
  )
}