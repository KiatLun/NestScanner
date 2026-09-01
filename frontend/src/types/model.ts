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

export interface TechnicalProfile {
  architecture: string | null
  parameterCount: string | null
  languages: string[]
  reportedWer: string | null
  fineTuningSupport: string | null
  license: string | null
}

export interface ResearchEvidenceItem {
  source: string
  title: string
  url: string
  description: string | null
  metadata: Record<string, unknown>
}

export interface ResearchEvidence {
  recencyEvidence: ResearchEvidenceItem[]
  deployabilityEvidence: ResearchEvidenceItem[]
  technicalEvidence: ResearchEvidenceItem[]
}

export interface ModelResearch {
  researchResultId: number
  scanId: number

  releaseDate: string | null
  isRecent: boolean | null
  isLocallyDeployable: boolean | null

  technicalProfile: TechnicalProfile | null
  // researchEvidence?: ResearchEvidence  
}

export interface ModelDetails extends StoredModel {
  research: ModelResearch | null
}