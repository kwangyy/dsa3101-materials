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

const KnowledgeGraph = ({ name }: { name: string }) => (
  <div className="w-full h-full bg-muted rounded-lg flex items-center justify-center">
    <p className="text-muted-foreground">Knowledge Graph: {name}</p>
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

export function KnowledgeGraphInterface() {
  const [messages, setMessages] = useState([
    { role: "system", content: "Welcome to the Knowledge Graph interface. How can I assist you?" },
  ])
  const [input, setInput] = useState("")
  const [graphs, setGraphs] = useState([
    { id: 1, name: "Graph 1" },
    { id: 2, name: "Graph 2" },
  ])
  const [selectedGraph, setSelectedGraph] = useState<{ id: number; name: string } | null>(null)
  const [newGraphName, setNewGraphName] = useState("")
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

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
      const newGraph = { id: Date.now(), name: newGraphName.trim() }
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

  return (
    <div className="flex h-screen max-h-screen">
      <div
        className={`bg-gray-800 text-white transition-all duration-300 ease-in-out ${
          isSidebarCollapsed ? 'w-0 min-w-0 overflow-hidden' : 'w-64 min-w-64'
        }`}
      >
        <div className="h-full flex flex-col relative">
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-2 right-2 z-10 text-white hover:bg-gray-700"
            onClick={toggleSidebar}
          >
            <ChevronLeft className="h-4 w-4" />
            <span className="sr-only">Collapse sidebar</span>
          </Button>
          <div className="p-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold mb-4">Knowledge Graphs</h2>
            <div className="flex space-x-2">
              <Input
                type="text"
                placeholder="New graph name"
                value={newGraphName}
                onChange={(e) => setNewGraphName(e.target.value)}
                className="bg-gray-700 text-white placeholder-gray-400 border-gray-600"
              />
              <Button onClick={handleAddGraph} className="bg-gray-700 hover:bg-gray-600">
                <Plus className="h-4 w-4" />
                <span className="sr-only">Add Graph</span>
              </Button>
            </div>
          </div>
          <ScrollArea className="flex-1">
            {graphs.map((graph) => (
              <div
                key={graph.id}
                className={`flex items-center justify-between p-2 hover:bg-gray-700 cursor-pointer ${
                  selectedGraph?.id === graph.id ? "bg-gray-700" : ""
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
                  className="text-white hover:bg-gray-600"
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
              <KnowledgeGraph name={selectedGraph.name} />
            ) : (
              <div className="h-full flex items-center justify-center">
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
    </div>
  )
}