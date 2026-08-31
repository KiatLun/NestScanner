import { ExternalLink } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button, buttonVariants } from "@/components/ui/button"
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

import type { StoredModel } from "@/types/model"

interface ModelsTableProps {
  models: StoredModel[]
}

export default function ModelsTable({
  models,
}: ModelsTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Discovered Models</CardTitle>

        <p className="text-sm text-muted-foreground">
          ASR models currently stored in the database.
        </p>
      </CardHeader>

      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Model</TableHead>
              <TableHead>Organisation</TableHead>
              <TableHead>Type</TableHead>
              <TableHead className="text-right">
                Link
              </TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {models.map((model) => (
              <TableRow key={model.modelId}>
                <TableCell>
                  <div>
                    <p className="font-medium">
                      {model.name}
                    </p>

                    <p className="text-xs text-muted-foreground">
                      ID: {model.modelId}
                    </p>
                  </div>
                </TableCell>

                <TableCell>
                  {model.organisation}
                </TableCell>

                <TableCell>
                  <Badge variant="outline">
                    {model.candidateType}
                  </Badge>
                </TableCell>

                <TableCell className="text-right">
                  <a
                    href={model.sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`Open ${model.name}`}
                    className={buttonVariants({
                      variant: "ghost",
                      size: "icon",
                    })}
                  >
                    <ExternalLink className="size-4" />
                  </a>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}