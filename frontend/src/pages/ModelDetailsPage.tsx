import {
  useEffect,
  useState,
} from "react"

import { useParams } from "react-router-dom"

import AppSidebar from "@/components/layout/AppSidebar"

import ModelHeader from "@/components/models/ModelHeader"
import ModelStatusCards from "@/components/models/ModelStatusCards"
import TechnicalProfileCard from "@/components/models/TechnicalProfileCard"

import type { ModelDetails } from "@/types/model"

import {
  getModelDetails,
} from "@/services/api"


function ModelDetailsPage() {
  const { modelId } = useParams()

  const [model, setModel] =
    useState<ModelDetails | null>(null)

  const [loading, setLoading] =
    useState(true)


  useEffect(() => {

    async function loadModel() {

      try {

        const data = await getModelDetails(
          Number(modelId)
        )

        setModel(data)

      } catch (error) {

        console.error(
          "Failed to load model:",
          error
        )

      } finally {

        setLoading(false)

      }
    }


    loadModel()

  }, [modelId])


  if (loading) {
    return (
      <div className="flex min-h-screen bg-muted/30">

        <AppSidebar />

        <main className="flex-1 p-8">

          <p className="text-muted-foreground">
            Loading model...
          </p>

        </main>

      </div>
    )
  }


  if (!model) {
    return (
      <div className="flex min-h-screen bg-muted/30">

        <AppSidebar />

        <main className="flex-1 p-8">

          <p className="text-muted-foreground">
            Model not found.
          </p>

        </main>

      </div>
    )
  }


  const profile =
    model.research?.technicalProfile


  return (
    <div className="flex min-h-screen bg-muted/30">

      <AppSidebar />


      <main className="min-w-0 flex-1">

        <div className="mx-auto max-w-7xl space-y-8 p-8">


          <ModelHeader
            model={model}
          />


          <ModelStatusCards
            research={model.research}
          />


          {profile && (
            <TechnicalProfileCard
              profile={profile}
            />
          )}


        </div>

      </main>

    </div>
  )
}


export default ModelDetailsPage