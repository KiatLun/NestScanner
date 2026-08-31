import { ExternalLink } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import type { ASRModel } from "@/types/model"

interface ModelsTableProps {
  models: ASRModel[]
}

function getUniqueSources(model: ASRModel): string[] {
  return [
    ...new Set(
      model.discoveryEvidence.map((evidence) => evidence.source)
    ),
  ]
}

export default function ModelsTable({
  models,
}: ModelsTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Discovered Models</CardTitle>

        <p className="text-sm text-muted-foreground">
          ASR candidates discovered from available research sources.
        </p>
      </CardHeader>

      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Model</TableHead>
              <TableHead>Organisation</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Sources</TableHead>
              <TableHead>Evidence</TableHead>
              <TableHead className="text-right">Link</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {models.map((model) => {
              const sources = getUniqueSources(model)

              return (
                <TableRow key={model.candidateId}>
                  <TableCell>
                    <div>
                      <p className="font-medium">
                        {model.candidate.name}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        ID: {model.candidateId}
                      </p>
                    </div>
                  </TableCell>

                  <TableCell>
                    {model.candidate.organisation}
                  </TableCell>

                  <TableCell>
                    <Badge variant="outline">
                      {model.candidate.candidateType}
                    </Badge>
                  </TableCell>

                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {sources.map((source) => (
                        <Badge
                          key={source}
                          variant="secondary"
                        >
                          {source}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>

                  <TableCell>
                    {model.discoveryEvidence.length}
                  </TableCell>

                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      asChild
                    >
                      <a
                        href={model.candidate.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label={`Open ${model.candidate.name}`}
                      >
                        <ExternalLink className="size-4" />
                      </a>
                    </Button>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}