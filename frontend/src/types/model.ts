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
  candidateId?: number
  candidate: ASRCandidate
  discoveryEvidence: DiscoveryEvidence[]
}

export interface DiscoveryResult {
  candidates: ASRModel[]
}

export interface DiscoverApiResponse {
  result: DiscoveryResult
}

export interface HuggingFaceModel {
  source: string
  title: string
  url: string
  description: string | null
  metadata: {
    createdAt: string | null
    downloads: number | null
    lastModified: string | null
    likes: number | null
    organisation: string | null
    pipelineTag: string | null
    tags: string[]
  }
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