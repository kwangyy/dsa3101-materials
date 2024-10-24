"use client"

import { useState } from "react"
import { Send, Plus, Trash2, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

const KnowledgeGraph = ({ name, data, onUploadClick }: { name: string; data: string | null; onUploadClick: () => void }) => (
  <div className="w-full h-full bg-muted rounded-lg flex flex-col items-center justify-center p-4">
    {data ? (
      <p className="text-muted-foreground">Knowledge Graph: {name}</p>
    ) : (
      <Button onClick={onUploadClick}>Upload</Button>
    )}
  </div>
)

const Statistics = () => (
  <div className="bg-muted p-4 rounded-lg">
    <h3 className="font-semibold mb-2">Statistics</h3>
    <ul className="space-y-1 text-sm">
      <li>Nodes: 1,234</li>
      <li>Edges: 5,678</li>
      <li>Queries: 9,012</li>
    </ul>
  </div>
)

const OntologySelection = ({ onCustomUpload, onGenerateOntology }: { onCustomUpload: (file: File) => void; onGenerateOntology: () => void }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white p-6 rounded-lg">
      <h2 className="text-xl font-bold mb-4">Select Ontology</h2>
      <Input
        type="file"
        accept=".txt,.owl"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file && (file.name.endsWith('.txt') || file.name.endsWith('.owl'))) {
            onCustomUpload(file);
          } else {
            alert('Please upload a .txt or .owl file.');
          }
        }}
        className="hidden"
        id="ontology-file-upload"
      />
      <div className="flex flex-col space-y-4">
        <Button variant="outline" onClick={() => document.getElementById('ontology-file-upload')?.click()}>
          Choose File
        </Button>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => document.getElementById('ontology-file-upload')?.click()} className="flex-1">
            Upload Custom Ontology
          </Button>
          <Button onClick={onGenerateOntology} className="flex-1">
            Use LLM-Generated Ontology
          </Button>
        </div>
      </div>
    </div>
  </div>
)

const UploadModal = ({ isOpen, onClose, onUpload }: { isOpen: boolean; onClose: () => void; onUpload: (file: File) => void }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Upload Data</h2>
        <Input
          type="file"
          accept=".txt"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file && file.name.endsWith('.txt')) {
              onUpload(file);
              onClose();
            } else {
              alert('Please upload a .txt file');
            }
          }}
          className="hidden"
          id="file-upload"
        />
        <div className="mt-4 flex justify-end">
          <Button onClick={onClose} variant="outline" className="mr-2">Cancel</Button>
          <Button onClick={() => document.getElementById('file-upload')?.click()} variant="outline">Select File</Button>
        </div>
      </div>
    </div>
  )
}

export function KnowledgeGraphInterface() {
  const [messages, setMessages] = useState([
    { role: "system", content: "Welcome to the Knowledge Graph interface. How can I assist you?" },
  ])
  const [input, setInput] = useState("")
  const [graphs, setGraphs] = useState([])
  const [selectedGraph, setSelectedGraph] = useState<{ id: number; name: string; data: string | null } | null>(null)
  const [newGraphName, setNewGraphName] = useState("")
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)
  const [showOntologySelection, setShowOntologySelection] = useState(false)

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
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const updatedGraphs = graphs.map(g => 
        g.id === selectedGraph?.id ? { ...g, data: text } : g
      )
      setGraphs(updatedGraphs)
      setSelectedGraph(prev => prev ? { ...prev, data: text } : null)
      setIsUploadModalOpen(false)
      setShowOntologySelection(true)
    }
    reader.readAsText(file)
  }

  return (
    <div className="flex h-screen max-h-screen">
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
            <h2 className="text-lg font-semibold mb-4">Knowledge Graphs</h2>
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
              <h2 className="text-lg font-semibold">Knowledge Graph</h2>
            </div>
            {selectedGraph ? (
              <KnowledgeGraph 
                name={selectedGraph.name} 
                data={selectedGraph.data} 
                onUploadClick={() => setIsUploadModalOpen(true)} 
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
          <div className="flex flex-col h-full">
            <div className="flex-1 p-4 flex flex-col">
              <h2 className="text-lg font-semibold mb-4">Search Interface</h2>
              <ScrollArea className="flex-1 pr-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`mb-4 ${
                      message.role === "user" ? "text-right" : "text-left"
                    }`}
                  >
                    <span
                      className={`inline-block p-2 rounded-lg ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      {message.content}
                    </span>
                  </div>
                ))}
              </ScrollArea>
              <Separator className="my-4" />
              <div className="flex items-center space-x-2">
                <Input
                  type="text"
                  placeholder="Search the knowledge graph..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSend()}
                />
                <Button onClick={handleSend}>
                  <Send className="h-4 w-4" />
                  <span className="sr-only">Send</span>
                </Button>
              </div>
            </div>
            <div className="p-4 border-t">
              <Statistics />
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
      <UploadModal 
        isOpen={isUploadModalOpen} 
        onClose={() => setIsUploadModalOpen(false)} 
        onUpload={handleDataUpload} 
      />
      {showOntologySelection && (
        <OntologySelection 
          onCustomUpload={(file) => {
            // Handle custom ontology upload
            // Process the ontology file here
            setShowOntologySelection(false)
          }}
          onGenerateOntology={() => {
            // Handle LLM-generated ontology
            // Generate or fetch the ontology here
            setShowOntologySelection(false)
          }}
        />
      )}
    </div>
  )
}
