"use client"

import { useState } from "react"
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

export function KnowledgeGraphInterface() {
  const { 
    graphs, 
    selectedGraph, 
    setGraphs, 
    setSelectedGraph, 
    addGraph, 
    deleteGraph 
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
      const newGraph = { id: Date.now(), name: newGraphName.trim(), data: null }
      setGraphs([...graphs, newGraph])
      setNewGraphName("")
      setSelectedGraph(newGraph)
    }
  }

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

  const handleDataUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setTempTextData(text);  // Store the text data temporarily
      setShowOntologySelection(true);  // Show ontology selection screen
      setIsUploadModalOpen(false);
    };
    reader.readAsText(file);
  };

  const transformGraphData = (apiResponse: any) => {
    const uniqueNodes = new Set<string>();
    apiResponse.forEach((item: any) => {
      uniqueNodes.add(item.head_node);
      uniqueNodes.add(item.tail_node);
    });

    const nodes = Array.from(uniqueNodes).map(id => ({
      id,
      details: {
        type: "Entity",
        connections: apiResponse.filter(item => 
          item.head_node === id || item.tail_node === id
        ).length,
        relationships: apiResponse
          .filter(item => item.head_node === id || item.tail_node === id)
          .map(item => item.relationship)
          .filter((value, index, self) => self.indexOf(value) === index) // Remove duplicates
      }
    }));
    const links = apiResponse.map((item: any) => ({
      source: item.head_node,
      target: item.tail_node,
      relationship: item.relationship
    }));

    return { nodes, links };
  };

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
            {graphs.map((graph) => (
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
              <KnowledgeGraphD3 
                nodes={selectedGraph.data?.nodes || []}
                links={selectedGraph.data?.links || []}
                onUploadClick={() => setIsUploadModalOpen(true)}
                data={selectedGraph.data}
                name={selectedGraph.name}
              />
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
          <ChatInterface
            messages={messages}
            input={input}
            onInputChange={(value) => setInput(value)}
            onSend={handleSend}
          />
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
                const response = await fetch('/api/process-data', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ 
                    data: tempTextData, 
                    ontology: ontologyText 
                  }),
                });
                
                const result = await response.json();
                if (result.error) throw new Error(result.error);
                
                const graphData = transformGraphData(result.entityResult);
                const updatedGraphs = graphs.map(g => 
                  g.id === selectedGraph?.id ? { ...g, data: graphData } : g
                );
                setGraphs(updatedGraphs);
                setSelectedGraph(prev => prev ? { ...prev, data: graphData } : null);
                setShowOntologySelection(false);
              } catch (error) {
                console.error('Error:', error);
              }
            };
            reader.readAsText(file);
          }}
          onGenerateOntology={async () => {
            try {
              const response = await fetch('/api/process-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  data: tempTextData, 
                  ontology: null 
                }),
              });
              
              const result = await response.json();
              if (result.error) throw new Error(result.error);
              
              const graphData = transformGraphData(result.entityResult);
              const updatedGraphs = graphs.map(g => 
                g.id === selectedGraph?.id ? { ...g, data: graphData } : g
              );
              setGraphs(updatedGraphs);
              setSelectedGraph(prev => prev ? { ...prev, data: graphData } : null);
              setShowOntologySelection(false);
            } catch (error) {
              console.error('Error:', error);
            }
          }}
        />
      )}
    </div>
  )
}
