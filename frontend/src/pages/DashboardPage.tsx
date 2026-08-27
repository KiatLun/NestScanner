import { useState } from 'react'
import { testLLM, getASRModels } from '../services/api'
import type { HuggingFaceModel } from '../types/model'
import { Button } from "@/components/ui/button"

const DashboardPage = () => {
  const [response, setResponse] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)
  const [models, setModels] = useState<HuggingFaceModel[]>([])
  const [modelsLoading, setModelsLoading] = useState<boolean>(false)

  async function handleTestLLM() {
    try {
      setLoading(true)

      const data = await testLLM()

      setResponse(data.response)
    } catch (error) {
      console.error(error)
      setResponse("Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  async function handleGetASRModels() {
    try {
      setModelsLoading(true)

      const data = await getASRModels()
      console.log("Fetched ASR models:", data.models)
      setModels(data.models)
    } catch (error) {
      console.error(error)
      setResponse("Something went wrong")
    } finally {
      setModelsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white p-8 text-slate-900">
      <h1 className="mb-6 text-4xl font-bold">
        ASR Research Dashboard
      </h1>

      <div className="flex gap-4">
        <Button
          onClick={handleTestLLM}
          disabled={loading}
        >
          {loading ? "Loading..." : "Test LLM"}
        </Button>

        <Button
          onClick={handleGetASRModels}
          disabled={modelsLoading}
          variant="secondary"
        >
          {modelsLoading ? "Loading..." : "Get ASR Models"}
        </Button>
      </div>

      <p className="mt-4">{response}</p>

      <ul className="mt-6">
        {models.map((model) => (
          <li key={model.url}>
            {model.title}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default DashboardPage