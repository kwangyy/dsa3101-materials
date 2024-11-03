import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface Graph {
  id: number;
  name: string;
  isLoading?: boolean;
  data: {
    nodes: Array<{id: string}>;
    links: Array<{source: string; target: string; relationship: string}>;
  } | null;
  metrics?: {
    accuracy?: number;
    completeness_score?: number;
    consistency_score?: number;
    overall_score?: number;
    valid_count?: number;
    invalid_count?: number;
    invalid_cases?: string[];
  };
}

interface GraphState {
  graphs: Graph[];
  selectedGraph: Graph | null;
  setGraphs: (graphs: Graph[]) => void;
  setSelectedGraph: (graph: Graph | null) => void;
  addGraph: (graph: Graph) => void;
  deleteGraph: (id: number) => void;
  updateGraph: (id: number, data: Partial<Graph>) => void;
}

export const useGraphStore = create<GraphState>()(
  persist(
    (set, get) => ({
      graphs: [],
      selectedGraph: null,
      setGraphs: (graphs) => {
        console.log('Setting graphs:', graphs);
        const currentSelectedId = get().selectedGraph?.id;
        set({ 
          graphs: Array.isArray(graphs) ? graphs : [],
          selectedGraph: currentSelectedId ? 
            (Array.isArray(graphs) ? graphs : []).find(g => g.id === currentSelectedId) || null 
            : null
        });
      },
      setSelectedGraph: (graph) => {
        console.log('Setting selected graph:', graph);
        set({ selectedGraph: graph });
      },
      addGraph: (graph) => set((state) => {
        console.log('Adding graph:', graph);
        const newGraphs = Array.isArray(state.graphs) ? [...state.graphs, graph] : [graph];
        return { 
          graphs: newGraphs,
          selectedGraph: graph 
        };
      }),
      deleteGraph: (id) => set((state) => ({
        graphs: Array.isArray(state.graphs) ? state.graphs.filter(g => g.id !== id) : [],
        selectedGraph: state.selectedGraph?.id === id ? null : state.selectedGraph
      })),
      updateGraph: (id, data) => set((state) => {
        const updatedGraphs = state.graphs.map(graph => {
          if (graph.id === id) {
            return { ...graph, ...data };
          }
          return graph;
        });
        return {
          graphs: updatedGraphs,
          selectedGraph: updatedGraphs.find(g => g.id === id) || null
        };
      }),
    }),
    {
      name: 'knowledge-graphs-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        graphs: state.graphs,
        selectedGraph: state.selectedGraph,
      }),
    }
  )
) 