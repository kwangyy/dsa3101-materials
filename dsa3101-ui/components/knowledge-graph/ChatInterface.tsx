import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Send } from "lucide-react"
import { Statistics } from "./Statistics"

interface Message {
  role: string;
  content: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
}

export const ChatInterface = ({ messages, input, onInputChange, onSend }: ChatInterfaceProps) => (
  <div className="flex flex-col h-full">
    <div className="flex-1 p-4 flex flex-col">
      <h2 className="text-lg font-semibold mb-4">Search Interface</h2>
      <ScrollArea className="flex-1 pr-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 ${message.role === "user" ? "text-right" : "text-left"}`}
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
          onChange={(e) => onInputChange(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && onSend()}
        />
        <Button onClick={onSend}>
          <Send className="h-4 w-4" />
          <span className="sr-only">Send</span>
        </Button>
      </div>
    </div>
    <div className="p-4 border-t">
      <Statistics />
    </div>
  </div>
)
