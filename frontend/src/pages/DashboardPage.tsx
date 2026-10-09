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


  // =================================================
  // FILTER / SORT STATE
  // =================================================

  const [sortBy, setSortBy] = useState<
    "downloads"
    | "likes"
    | "createdAt"
    | "lastModified"
  >("downloads")

  const [sortOrder, setSortOrder] = useState<
    "desc"
    | "asc"
  >("desc")

  const [organisationFilter, setOrganisationFilter] =
    useState<string>("all")

  const [deploymentFilter, setDeploymentFilter] =
    useState<string>("all")


  // =================================================
  // FETCH MODELS
  // =================================================

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


      setModels(
        modelsWithDeploymentStatus
      )

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


  // =================================================
  // RUN SCAN
  // =================================================

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


  // =================================================
  // ORGANISATION OPTIONS
  // =================================================

  const organisationsList =
    Array.from(
      new Set(
        models
          .map(
            (model) =>
              model.organisation
          )
          .filter(Boolean)
      )
    ).sort()


  // =================================================
  // FILTER + SORT MODELS
  // =================================================

  const displayedModels =
    [...models]

      .filter((model) => {

        if (
          organisationFilter ===
          "all"
        ) {
          return true
        }

        return (
          model.organisation ===
          organisationFilter
        )
      })

      .filter((model) => {

        if (
          deploymentFilter ===
          "all"
        ) {
          return true
        }

        return (
          model.deploymentStatus ===
          deploymentFilter
        )
      })

      .sort((a, b) => {

        let comparison = 0


        // -----------------------------------------
        // NUMBER SORTING
        // -----------------------------------------

        if (
          sortBy === "downloads" ||
          sortBy === "likes"
        ) {

          const aValue =
            a[sortBy] ?? 0

          const bValue =
            b[sortBy] ?? 0

          comparison =
            aValue - bValue
        }


        // -----------------------------------------
        // DATE SORTING
        // -----------------------------------------

        if (
          sortBy === "createdAt" ||
          sortBy === "lastModified"
        ) {

          const aValue =
            a[sortBy]
              ? new Date(
                  a[sortBy]!
                ).getTime()
              : 0

          const bValue =
            b[sortBy]
              ? new Date(
                  b[sortBy]!
                ).getTime()
              : 0

          comparison =
            aValue - bValue
        }


        return sortOrder === "desc"
          ? -comparison
          : comparison
      })


  // =================================================
  // STATISTICS
  // =================================================

  const organisations =
    new Set(
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


          {/* =========================================
              HEADER
          ========================================= */}

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


          {/* =========================================
              FILTERS
          ========================================= */}

          <div className="flex flex-wrap gap-4">

            {/* ORGANISATION */}

            <div>

              <label className="text-sm font-medium">
                Organisation
              </label>

              <select
                value={organisationFilter}
                onChange={(event) =>
                  setOrganisationFilter(
                    event.target.value
                  )
                }
                className="mt-1 block rounded-md border bg-background px-3 py-2 text-sm"
              >

                <option value="all">
                  All organisations
                </option>

                {organisationsList.map(
                  (organisation) => (

                    <option
                      key={organisation}
                      value={organisation}
                    >
                      {organisation}
                    </option>

                  )
                )}

              </select>

            </div>


            {/* DEPLOYMENT */}

            <div>

              <label className="text-sm font-medium">
                Deployment
              </label>

              <select
                value={deploymentFilter}
                onChange={(event) =>
                  setDeploymentFilter(
                    event.target.value
                  )
                }
                className="mt-1 block rounded-md border bg-background px-3 py-2 text-sm"
              >

                <option value="all">
                  All models
                </option>

                <option value="deployed">
                  Deployed
                </option>

                <option value="not_deployed">
                  Not deployed
                </option>

              </select>

            </div>


            {/* SORT BY */}

            <div>

              <label className="text-sm font-medium">
                Sort by
              </label>

              <select
                value={sortBy}
                onChange={(event) =>
                  setSortBy(
                    event.target.value as
                      | "downloads"
                      | "likes"
                      | "createdAt"
                      | "lastModified"
                  )
                }
                className="mt-1 block rounded-md border bg-background px-3 py-2 text-sm"
              >

                <option value="downloads">
                  Downloads
                </option>

                <option value="likes">
                  Likes
                </option>

                <option value="createdAt">
                  Created date
                </option>

                <option value="lastModified">
                  Last modified
                </option>

              </select>

            </div>


            {/* SORT ORDER */}

            <div>

              <label className="text-sm font-medium">
                Order
              </label>

              <select
                value={sortOrder}
                onChange={(event) =>
                  setSortOrder(
                    event.target.value as
                      | "asc"
                      | "desc"
                  )
                }
                className="mt-1 block rounded-md border bg-background px-3 py-2 text-sm"
              >

                <option value="desc">
                  Highest / Newest
                </option>

                <option value="asc">
                  Lowest / Oldest
                </option>

              </select>

            </div>

          </div>


          {/* =========================================
              MODEL TABLE
          ========================================= */}

          <ModelsTable
            models={displayedModels}
          />


          {/* =========================================
              STAT CARDS
          ========================================= */}

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