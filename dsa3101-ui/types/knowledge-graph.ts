export interface Node {
  id: string;
  details?: {
    [key: string]: any;
  };
}

export interface Link {
  source: string;
  target: string;
  relationship: string;
}

export interface KnowledgeGraphProps {
  nodes: Node[];
  links: Link[];
  onUploadClick: () => void;
  data: any;
  name: string;
}
