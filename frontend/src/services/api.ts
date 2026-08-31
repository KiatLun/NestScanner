import type { HuggingFaceModel } from "../types/model";
import type { ASRModel, DiscoverApiResponse, Scan, AllScans} from "../types/model";

const API_BASE_URL = "http://localhost:8000";

export interface LLMResponse {
  response: string;
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

export async function discoverASRModels(): Promise<ASRModel[]> {
  const response = await fetch(`${API_BASE_URL}/api/discover`);
  if (!response.ok) {
    throw new Error("Failed to discover ASR models");
  }
  const data: DiscoverApiResponse = await response.json();
  console.log("Discovered ASR models:", data.result.candidates);
  return data.result.candidates;
}

export async function getAllScans(): Promise<Scan[]> {
  const response = await fetch(`${API_BASE_URL}/api/getAllScans`);
  if (!response.ok) {
    throw new Error("Failed to fetch scans");
  }
  const data: AllScans = await response.json();
  return data.scans;
}

export async function getScanById(scanId: number): Promise<Scan> {
  const response = await fetch(`${API_BASE_URL}/api/getScanById/${scanId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scan with ID ${scanId}`);
  }
  const data: Scan = await response.json();
  return data;
}