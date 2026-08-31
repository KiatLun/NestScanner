export interface ASRCandidate {
  name: string
  organisation: string | null
  sourceUrl: string
  reason?: string
  candidateType: string
}

export interface DiscoveryEvidence {
  source: string
  title: string
  url: string
  description: string | null
  metadata: Record<string, unknown>
}

export interface ASRModel {
  modelId: number
  candidate: ASRCandidate
  discoveryEvidence: DiscoveryEvidence[]
}

export interface DiscoveryResult {
  candidates: ASRModel[]
}

export interface DiscoverApiResponse {
  result: DiscoveryResult
}



export interface Scan {
  id: number
  query: string
  started_at: string
  completed_at: string | null
  //status?: "pending" | "in_progress" | "completed" | "failed"
}

export interface AllScans {
  scans: Scan[]
}

export interface StoredModel {
  modelId: number
  name: string
  organisation: string
  sourceUrl: string
  candidateType: string
}

export interface startScanResponse {
  scanId: number
  query: string
  status: "running"
  stage: string
  discoveryConfig: Record<string, unknown>
  researchConfig: Record<string, unknown>
}

export interface scanStatusResponse {
  scanId: number,
  status: "running" | "completed" | "failed"
  stage: string
  error: string | null
  started_at: string
  completed_at: string | null
}