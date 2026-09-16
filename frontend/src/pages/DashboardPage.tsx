import {
  useState,
  useEffect,
} from "react"

import AppSidebar from "@/components/layout/AppSidebar"
import ModelsTable from "@/components/dashboard/ModelsTable"
import StatCard from "@/components/dashboard/StatCard"
import { Button } from "@/components/ui/button"

import {
  Database,
  Layers3,
  Sparkles,
} from "lucide-react"

import type {
  ModelWithDeploymentStatus,
} from "@/types/model"

import {
  getAllModels,
  startScan,
  waitforScanCompletion,
  getAllEchoforgeModels,
} from "@/services/api"

function DashboardPage() {
  const [models, setModels] =
    useState<ModelWithDeploymentStatus[]>([])

  const [loading, setLoading] =
    useState(false)

  async function fetchModels() {
    try {
      const [
        allModels,
        echoforgeData,
      ] = await Promise.all([
        getAllModels(),
        getAllEchoforgeModels(),
      ])

      const deployedRepositoryIds =
        new Set(
          echoforgeData.models
            .filter(
              (model) =>
                model.sourceType
                  .toLowerCase() ===
                "huggingface"
            )
            .map(
              (model) =>
                model.source
                  .trim()
                  .toLowerCase()
            )
        )

      const modelsWithDeploymentStatus:
        ModelWithDeploymentStatus[] =
        allModels.map(
          (model): ModelWithDeploymentStatus => ({
            ...model,

            deploymentStatus:
              model.repositoryId &&
              deployedRepositoryIds.has(
                model.repositoryId
                  .trim()
                  .toLowerCase()
              )
                ? "deployed"
                : "not_deployed",
          })
        )

      setModels(modelsWithDeploymentStatus)

    } catch (error) {
      console.error(
        "Failed to fetch models:",
        error
      )
    }
  }

  useEffect(() => {
    fetchModels()
  }, [])

  async function handleScan() {
    try {
      setLoading(true)

      const scan = await startScan()

      console.log(
        "Scan started:",
        scan
      )

      const finalStatus =
        await waitforScanCompletion(
          scan.scanId
        )

      console.log(
        "Scan completed:",
        finalStatus
      )

      if (
        finalStatus.status ===
        "completed"
      ) {
        await fetchModels()
      }

    } catch (error) {
      console.error(
        "Scan failed:",
        error
      )

    } finally {
      setLoading(false)
    }
  }

  const organisations = new Set(
    models
      .map(
        (model) =>
          model.organisation
      )
      .filter(Boolean)
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

          <ModelsTable
            models={models}
          />

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard
              title="Models"
              value={models.length}
              description="ASR models discovered"
              icon={Database}
            />

            <StatCard
              title="Organisations"
              value={organisations}
              description="Distinct organisations found"
              icon={Layers3}
            />
          </div>
        </div>
      </main>
    </div>
  )
}

export default DashboardPage