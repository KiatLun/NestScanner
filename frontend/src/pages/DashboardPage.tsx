import { useState } from "react"

import AppSidebar from "@/components/layout/AppSidebar"
import ModelsTable from "@/components/dashboard/ModelsTable"
import StatCard from "@/components/dashboard/StatCard"
import { Button } from "@/components/ui/button"

import SampleOutput from "@/mock/sampleOutput.json"

import {
  Database,
  FileSearch,
  Layers3,
  Sparkles,
} from "lucide-react"

import type { ASRModel } from "@/types/model"

import {discoverASRModels} from "@/services/api"

function DashboardPage() {
  const [models, setModels] = useState<ASRModel[]>([])
  const [loading, setLoading] = useState(false)

  async function handleScan() {
    try {
      setLoading(true)

      //const discoveredModels = await discoverASRModels();
      const discoveredModels: ASRModel[] = SampleOutput.candidates;
      setModels(discoveredModels);
    } catch (error) {
      console.error("Scan failed:", error)
    } finally {
      setLoading(false)
    }
  }

  const evidenceCount = models.reduce(
    (total, model) =>
      total + model.discoveryEvidence.length,
    0
  )

  const organisations = new Set(
    models.map(
      (model) => model.candidate.organisation
    )
  ).size

  return (
    <div className="flex min-h-screen bg-muted/30">
      <AppSidebar />

      <main className="min-w-0 flex-1">
        <div className="mx-auto max-w-7xl space-y-8 p-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                ASR Model Intelligence
              </h1>

              <p className="mt-1 text-muted-foreground">
                Scan and analyse speech recognition models.
              </p>
            </div>

            <Button
              onClick={handleScan}
              disabled={loading}
              className="gap-2"
            >
              <Sparkles className="size-4" />

              {loading
                ? "Scanning..."
                : "Run Scan"}
            </Button>
          </div>

          <ModelsTable models={models} />
          
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard
              title="Candidates"
              value={models.length}
              description="ASR candidates discovered"
              icon={Database}
            />

            <StatCard
              title="Evidence"
              value={evidenceCount}
              description="Supporting discovery evidence"
              icon={FileSearch}
            />

            <StatCard
              title="Organisations"
              value={organisations}
              description="Distinct organisations found"
              icon={Layers3}
            />

            <StatCard
              title="Sources"
              value={
                new Set(
                  models.flatMap((model) =>
                    model.discoveryEvidence.map(
                      (evidence) => evidence.source
                    )
                  )
                ).size
              }
              description="Discovery sources represented"
              icon={Sparkles}
            />
          </div>


        </div>
      </main>
    </div>
  )
}

export default DashboardPage