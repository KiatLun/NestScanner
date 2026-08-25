const API_BASE_URL = "http://localhost:8000";

export interface LLMResponse {
  response: string;
}

export interface HuggingFaceModel {
  id: string;
  author: string | null;
  downloads: number | null;
  likes: number | null;
  pipeline_tag: string | null;
  last_modified: string | null;
}

export interface HuggingFaceModelResponse {
  models: HuggingFaceModel[];
}

export async function testLLM(): Promise<LLMResponse> {
  const response = await fetch(`${API_BASE_URL}/api/test-llm`);

  if (!response.ok) {
    throw new Error("Failed to call backend");
  }

  return response.json();
}

export async function getASRModels(): Promise<HuggingFaceModelResponse> {
  const response = await fetch(`${API_BASE_URL}/api/huggingface/asr-models`);

  if (!response.ok) {
    throw new Error("Failed to fetch ASR models from Hugging Face");
  }

  return response.json();
}