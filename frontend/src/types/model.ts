export interface ASRCandidate {
  name: string
  organisation: string | null
  sourceUrl: string
  reason?: string
  repositoryId: string
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
}


export interface AllScans {
  scans: Scan[]
}


export interface StoredModel {
  modelId: number
  name: string
  organisation: string
  sourceUrl: string
  repositoryId: string | null

  createdAt: string | null
  downloads: number | null
  lastModified: string | null
  likes: number | null
  pipelineTag: string | null
  revision: string | null
  tags: string[]
  trendingScore: number | null
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
  scanId: number
  status: "running" | "completed" | "failed"
  stage: string
  error: string | null
  started_at: string
  completed_at: string | null
}


export interface TechnicalProfile {
  architecture: string | null
  parameterCount: string | number| null
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
  deployabilityEvidence: ResearchEvidenceItem[]
  technicalEvidence: ResearchEvidenceItem[]
}


export interface ModelResearch {
  researchResultId: number
  scanId: number
  releaseDate: string | null
  isLocallyDeployable: boolean | null
  technicalProfile: TechnicalProfile | null
  // researchEvidence?: ResearchEvidence
}


export interface ModelDetails extends StoredModel {
  research: ModelResearch | null
}


export type DeploymentStatus = "deployed" | "not_deployed"


export interface ModelWithDeploymentStatus extends StoredModel {
  deploymentStatus: DeploymentStatus
}


export interface EchoforgeModel {
  source: string
  cacheName: string
  downloader: string
  scope: string
  sourceType: string
}


export interface EchoforgeModelsResponse {
  models: EchoforgeModel[]
  count: number
}