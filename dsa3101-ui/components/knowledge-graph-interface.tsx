"use client"

import { useState, useEffect } from "react"
import { Plus, Trash2, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { ChatInterface } from "./chat/ChatInterface"
import { OntologySelection } from "./knowledge-graph/OntologySelection"
import { UploadModal } from "./knowledge-graph/UploadModal"
import KnowledgeGraphD3 from "./KnowledgeGraphD3"
import { useGraphStore } from "../stores/graphStore"
import { Statistics } from "./chat/Statistics"

export function KnowledgeGraphInterface() {
  const { 
    graphs = [],
    selectedGraph, 
    setGraphs, 
    setSelectedGraph, 
    addGraph, 
    deleteGraph,
    updateGraph
  } = useGraphStore();

  const [messages, setMessages] = useState([
    { role: "system", content: "Welcome to the Knowledge Graph interface. How can I assist you?" },
  ]);
  const [input, setInput] = useState("");
  const [newGraphName, setNewGraphName] = useState("");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [showOntologySelection, setShowOntologySelection] = useState(false);
  const [tempTextData, setTempTextData] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<any>(null);

  // Handlers from original component
  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, { role: "user", content: input }])
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { role: "system", content: `Here's some information about "${input}"...` },
        ])
      }, 1000)
      setInput("")
    }
  }

  const handleAddGraph = () => {
    if (newGraphName.trim()) {
      const newGraph: Graph = {
        id: Date.now(),
        name: newGraphName.trim(),
        data: null,
        isLoading: false
      };
      addGraph(newGraph);
      setNewGraphName("");
      setSelectedGraph(newGraph);
    }
  };

  const handleDeleteGraph = (id: number) => {
    const updatedGraphs = graphs.filter(graph => graph.id !== id)
    setGraphs(updatedGraphs)
    if (selectedGraph?.id === id) {
      setSelectedGraph(null)
    }
  }

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed)
  }

  const handleDataUpload = async (file: File) => {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target?.result as string;
      try {
        const uploadResponse = await fetch('/api/process-data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data: text }),
        });
        
        const uploadResult = await uploadResponse.json();
        if (uploadResult.error) throw new Error(uploadResult.error);
        
        if (!selectedGraph) {
          alert('Please select or create a graph first');
          return;
        }
        
        setTempTextData(uploadResult.graphId);
        setShowOntologySelection(true);
        setIsUploadModalOpen(false);
      } catch (error) {
        console.error('Error uploading data:', error);
        alert('Error uploading data: ' + error);
      }
    };
    reader.readAsText(file);
  };

  const transformGraphData = (apiResponse: any) => {
    const uniqueNodes = new Set<string>();
    const relationships = apiResponse.relationships || [];

    relationships.forEach((item: any) => {
      // Get the second and third keys (after 'type')
      const keys = Object.keys(item).filter(k => k !== 'type');
      const headKey = keys[0];
      const tailKey = keys[1];
      
      // Add both nodes to the set
      uniqueNodes.add(item[headKey]);
      uniqueNodes.add(item[tailKey]);
    });

    const nodes = Array.from(uniqueNodes).map(id => ({
      id,
      details: {
        type: "Entity",
        connections: relationships.filter(item => {
          const keys = Object.keys(item).filter(k => k !== 'type');
          return item[keys[0]] === id || item[keys[1]] === id;
        }).length,
        relationships: relationships
          .filter(item => {
            const keys = Object.keys(item).filter(k => k !== 'type');
            return item[keys[0]] === id || item[keys[1]] === id;
          })
          .map(item => item.type)
          .filter((value, index, self) => self.indexOf(value) === index)
      }
    }));

    const links = relationships.map((item: any) => {
      const keys = Object.keys(item).filter(k => k !== 'type');
      return {
        source: item[keys[0]], // head node
        target: item[keys[1]], // tail node
        relationship: item.type
      };
    });

    return { nodes, links };
  };

  useEffect(() => {
    console.log('Current graphs:', graphs);
    console.log('Selected graph:', selectedGraph);
  }, [graphs, selectedGraph]);

  return (
    <div className="flex h-screen max-h-screen">
      {/* Sidebar */}
      <div
        className={`bg-gray-100 text-gray-800 transition-all duration-300 ease-in-out ${
          isSidebarCollapsed ? 'w-0 min-w-0 overflow-hidden' : 'w-64 min-w-64'
        }`}
      >
        <div className="h-full flex flex-col relative">
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-2 right-2 z-10 text-gray-600 hover:bg-gray-200"
            onClick={toggleSidebar}
          >
            <ChevronLeft className="h-4 w-4" />
            <span className="sr-only">Collapse sidebar</span>
          </Button>
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold mb-4">node.py</h2>
            <div className="flex space-x-2">
              <Input
                type="text"
                placeholder="New graph name"
                value={newGraphName}
                onChange={(e) => setNewGraphName(e.target.value)}
                className="flex-grow bg-white text-gray-800 placeholder-gray-400 border-gray-300"
              />
              <Button 
                onClick={handleAddGraph} 
                className="bg-white hover:bg-gray-100 text-gray-800"
                size="icon"
              >
                <Plus className="h-4 w-4" />
                <span className="sr-only">Add Graph</span>
              </Button>
            </div>
          </div>
          <ScrollArea className="flex-1">
            {Array.isArray(graphs) && graphs.map((graph) => (
              <div
                key={graph.id}
                className={`flex items-center justify-between p-2 hover:bg-gray-200 cursor-pointer ${
                  selectedGraph?.id === graph.id ? "bg-gray-200" : ""
                }`}
                onClick={() => setSelectedGraph(graph)}
              >
                <span>{graph.name}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteGraph(graph.id)
                  }}
                  className="text-gray-600 hover:bg-gray-300"
                >
                  <Trash2 className="h-4 w-4" />
                  <span className="sr-only">Delete {graph.name}</span>
                </Button>
              </div>
            ))}
          </ScrollArea>
        </div>
      </div>

      <ResizablePanelGroup direction="horizontal" className="flex-1">
        <ResizablePanel defaultSize={50}>
          <div className="p-4 h-full relative">
            {/* Knowledge Graph Panel */}
            <div className="flex items-center mb-4">
              {isSidebarCollapsed && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="mr-2"
                  onClick={toggleSidebar}
                >
                  <ChevronRight className="h-4 w-4" />
                  <span className="sr-only">Expand sidebar</span>
                </Button>
              )}
              <h2 className="text-lg font-semibold flex-grow">Knowledge Graph</h2>
            </div>
            {selectedGraph ? (
              <div className="flex flex-col h-full">
                <KnowledgeGraphD3 
                  nodes={selectedGraph.data?.nodes || []}
                  links={selectedGraph.data?.links || []}
                  onUploadClick={() => setIsUploadModalOpen(true)}
                  data={selectedGraph.data}
                  name={selectedGraph.name}
                  isLoading={selectedGraph.isLoading}
                />
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <p className="text-muted-foreground">Select or create a graph</p>
              </div>
            )}
          </div>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={50}>
          {/* Chat Interface */}
          <div className="flex flex-col h-full">
            <ChatInterface
              messages={messages}
              input={input}
              onInputChange={(value) => setInput(value)}
              onSend={handleSend}
            />
            <div className="p-4 border-t">
              <Statistics 
                metrics={selectedGraph?.metrics}
                graphData={selectedGraph?.data}
              />
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>

      {/* Modals */}
      <UploadModal 
        isOpen={isUploadModalOpen} 
        onClose={() => setIsUploadModalOpen(false)} 
        onUpload={handleDataUpload} 
      />
      {showOntologySelection && (
        <OntologySelection 
        onCustomUpload={async (file) => {
          const reader = new FileReader();
          reader.onload = async (e) => {
            const ontologyText = e.target?.result as string;
            try {
              if (!selectedGraph) {
                alert('No graph selected');
                return;
              }

              // Update loading state
              const graphId = selectedGraph.id;
              const updatedGraph = { 
                ...selectedGraph, 
                isLoading: true,
                data: null
              };
              updateGraph(graphId, updatedGraph);

              const response = await fetch('/api/process-ontology', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  graphId: tempTextData,
                  ontology: JSON.parse(ontologyText),
                }),
              });
              
              const result = await response.json();
              
              if (result.error) {
                console.error('Error:', result.error);
                alert('Error processing ontology: ' + result.error);
                setShowOntologySelection(false);
                updateGraph(graphId, { isLoading: false });
                return;
              }

              const graphData = transformGraphData(result.entityResult);
              
              // Update graph with new data
              const finalGraph = {
                ...selectedGraph,
                data: graphData,
                metrics: result.metrics,
                isLoading: false
              };
              
              updateGraph(graphId, finalGraph);
              setMetrics(result.metrics);
              setShowOntologySelection(false);
            } catch (error) {
              console.error('Error:', error);
              alert('Error processing ontology: ' + error);
              setShowOntologySelection(false);
              if (selectedGraph) {
                updateGraph(selectedGraph.id, { isLoading: false });
              }
            }
          };
          reader.readAsText(file);
        }}
          onGenerateOntology={async () => {
            try {
              if (!selectedGraph) {
                alert('No graph selected');
                return;
              }

              // Set loading state
              setGraphs(prev => prev.map(g => 
                g.id === selectedGraph.id 
                  ? { ...g, isLoading: true, data: null }
                  : g
              ));

              const response = await fetch('/api/process-ontology', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  graphId: selectedGraph.id,
                  ontology: null 
                }),
              });
              
              const result = await response.json();
              if (result.error) throw new Error(result.error);
              
              const graphData = transformGraphData(result.entityResult);
              
              // Update graphs with new data
              setGraphs(prev => {
                const updatedGraphs = prev.map(g => 
                  g.id === selectedGraph.id 
                    ? { 
                        ...g, 
                        data: graphData,
                        metrics: result.metrics,
                        isLoading: false
                      } 
                    : g
                );
                console.log('Updated graphs:', updatedGraphs);
                return updatedGraphs;
              });

              setMetrics(result.metrics);
              setShowOntologySelection(false);
            } catch (error) {
              console.error('Error:', error);
              // Reset loading state on error
              setGraphs(prev => prev.map(g => 
                g.id === selectedGraph?.id 
                  ? { ...g, isLoading: false }
                  : g
              ));
            }
          }}
        />
      )}
    </div>
  )
}
