export interface ASRModel {
  id: string;
  name: string;
  provider: string;
  source: string;
  releasedAt: string;

  description?: string;

  downloads?: number;
  languages?: string[];
  tags?: string[];

  modelUrl?: string;
}

export interface HuggingFaceModel {
  source: string;
  title: string;
  url: string;
  description: string | null;

  metadata: {
    createdAt: string | null;
    downloads: number | null;
    lastModified: string | null;
    likes: number | null;
    organisation: string | null;
    pipelineTag: string | null;
    tags: string[];
  };
}