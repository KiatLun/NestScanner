import { ExternalLink } from "lucide-react"
import {Link} from "react-router-dom"

import { Badge } from "@/components/ui/badge"
import { buttonVariants } from "@/components/ui/button"
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
        <Table
          containerClassName="max-h-[500px] overflow-auto"
          className="min-w-[600px]"
        >
          <TableHeader className="sticky top-0 z-20 bg-card">
            <TableRow>
              <TableHead className="min-w-[250px]">
                Model
              </TableHead>

              <TableHead className="min-w-[180px]">
                Organisation
              </TableHead>

              <TableHead className="min-w-[150px]">
                Type
              </TableHead>

              <TableHead className="w-[80px] text-right">
                Link
              </TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {models.map((model) => (
              <TableRow key={model.modelId}>
                <TableCell>
                  <div>
                    <Link
                      to={`/models/${model.modelId}`}
                      className="font-medium hover:underline"
                    >
                      {model.name}
                    </Link>

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