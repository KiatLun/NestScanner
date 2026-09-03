import type { ModelDetails, scanStatusResponse, startScanResponse, StoredModel } from "../types/model";
import type { Scan, AllScans} from "../types/model";

const API_BASE_URL = "http://localhost:8000";

export interface LLMResponse {
  response: string;
}


export async function testLLM(): Promise<LLMResponse> {
  const response = await fetch(`${API_BASE_URL}/api/test-llm`);

  if (!response.ok) {
    throw new Error("Failed to call backend");
  }

  return response.json();
}


export async function getAllModels(): Promise<StoredModel[]> {
  const response = await fetch(`${API_BASE_URL}/api/getAllModels`);
  if (!response.ok) {
    throw new Error("No Models found in database");
  }
  const data = await response.json();
  return data.models;
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

export async function startScan(): Promise<startScanResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/startScan`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: "Find recent automatic speech recognition models.",
      }),
    }
  )

  if (!response.ok) {
    throw new Error("Failed to start scan")
  }

  const data = await response.json()

  if (
    data.status !== "running" ||
    typeof data.scanId !== "number"
  ) {
    throw new Error("Scan did not start correctly")
  }

  return data
}

export async function getScanStatus(scanId: number): Promise<scanStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/getScanStatus/${scanId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scan status for ID ${scanId}`);
  }
  const data: scanStatusResponse = await response.json();
  return data;
}

export async function waitforScanCompletion(scanId: number): Promise<scanStatusResponse> {
  while (true) {
    const statusResponse = await getScanStatus(scanId);
    if (statusResponse.status === "completed" || statusResponse.status === "failed") {
      return statusResponse;
    }
    await new Promise((resolve) => setTimeout(resolve, 3000)); // Wait for 3 seconds before checking again
  }
}

export async function getModelDetails(
  modelId: number
): Promise<ModelDetails> {

  const response = await fetch(
    `${API_BASE_URL}/api/getModelDetails/${modelId}`
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load model ${modelId}`
    )
  }

  return response.json()
}