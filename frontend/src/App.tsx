import { useState } from "react";
import { 
  testLLM,
  getASRModels,
} from "./services/api";

import type { HuggingFaceModel } from "./types/model";

function App() {
  const [response, setResponse] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [models, setModels] = useState<HuggingFaceModel[]>([]);
  const [modelsLoading, setModelsLoading] = useState<boolean>(false);

  async function handleTestLLM() {
    try {
      setLoading(true);

      const data = await testLLM();

      setResponse(data.response);
    } catch (error) {
      console.error(error);
      setResponse("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleGetASRModels() {
    try {
      setModelsLoading(true);

      const data = await getASRModels();
      console.log("Fetched ASR models:", data.models);
      setModels(data.models);
    } catch (error) {
      console.error(error);
      setResponse("Something went wrong");
    } finally {
      setModelsLoading(false);
    }
  }

  return (
    <div>
      <h1>ASR Research Dashboard</h1>

      <button onClick={handleTestLLM}>
        {loading ? "Loading..." : "Test LLM"}
      </button>

      <p>{response}</p>

      <button onClick={handleGetASRModels}>
        {modelsLoading ? "Loading..." : "Get ASR Models"}
      </button>
      
      <ul>
        {models.map((model) => (
          <li key={model.url}>
            {model.title}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;