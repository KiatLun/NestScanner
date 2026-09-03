import { useEffect, useState } from "react"
import { Clock, History, Loader2 } from "lucide-react"

import AppSidebar from "@/components/layout/AppSidebar"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import { Badge } from "@/components/ui/badge"

import type { Scan } from "@/types/model"
import { getAllScans } from "@/services/api"

function HistoryPage() {
  const [scans, setScans] = useState<Scan[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadScans() {
      try {
        const scanHistory = await getAllScans()
        setScans(scanHistory)
      } catch (error) {
        console.error("Failed to load scan history:", error)
      } finally {
        setLoading(false)
      }
    }

    loadScans()
  }, [])

  function formatDate(date: string) {
    return new Date(date).toLocaleString()
  }

  return (
    <div className="flex min-h-screen bg-muted/30">
      <AppSidebar />

      <main className="min-w-0 flex-1">
        <div className="mx-auto max-w-7xl space-y-8 p-8">
          <div>
            <div className="flex items-center gap-3">
              <History className="size-7" />

              <h1 className="text-3xl font-bold tracking-tight">
                Scan History
              </h1>
            </div>

            <p className="mt-1 text-muted-foreground">
              View previous ASR model discovery scans.
            </p>
          </div>

          <div className="rounded-lg border bg-background">
            {loading ? (
              <div className="flex h-48 items-center justify-center">
                <Loader2 className="size-6 animate-spin text-muted-foreground" />
              </div>
            ) : scans.length === 0 ? (
              <div className="flex h-48 flex-col items-center justify-center text-muted-foreground">
                <Clock className="mb-2 size-8" />

                <p>No scan history found.</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">
                      Scan ID
                    </TableHead>

                    <TableHead>
                      Query
                    </TableHead>

                    <TableHead>
                      Started
                    </TableHead>

                    <TableHead>
                      Completed
                    </TableHead>

                    <TableHead>
                      Status
                    </TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {scans.map((scan) => (
                    <TableRow key={scan.id}>
                      <TableCell className="font-medium">
                        #{scan.id}
                      </TableCell>

                      <TableCell>
                        {scan.query}
                      </TableCell>

                      <TableCell>
                        {formatDate(scan.started_at)}
                      </TableCell>

                      <TableCell>
                        {scan.completed_at
                          ? formatDate(scan.completed_at)
                          : "—"}
                      </TableCell>

                      <TableCell>
                        {scan.completed_at ? (
                          <Badge variant="secondary">
                            Completed
                          </Badge>
                        ) : (
                          <Badge variant="outline">
                            Running
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default HistoryPage