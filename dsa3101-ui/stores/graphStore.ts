import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface Graph {
  id: number;
  name: string;
  data: {
    nodes: Array<{id: string}>;
    links: Array<{source: string; target: string; relationship: string}>;
  } | null;
}

interface GraphState {
  graphs: Graph[];
  selectedGraph: Graph | null;
  setGraphs: (graphs: Graph[]) => void;
  setSelectedGraph: (graph: Graph | null) => void;
  addGraph: (graph: Graph) => void;
  deleteGraph: (id: number) => void;
}

export const useGraphStore = create<GraphState>()(
  persist(
    (set) => ({
      graphs: [],
      selectedGraph: null,
      setGraphs: (graphs) => set({ graphs }),
      setSelectedGraph: (graph) => set({ selectedGraph: graph }),
      addGraph: (graph) => set((state) => ({ 
        graphs: [...state.graphs, graph] 
      })),
      deleteGraph: (id) => set((state) => ({
        graphs: state.graphs.filter(g => g.id !== id),
        selectedGraph: state.selectedGraph?.id === id ? null : state.selectedGraph
      })),
    }),
    {
      name: 'knowledge-graphs-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
) 