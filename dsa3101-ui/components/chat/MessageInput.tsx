import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Send } from "lucide-react"
import { MessageInputProps } from "@/types/chat"

export const MessageInput = ({ value, onChange, onSend }: MessageInputProps) => (
  <div className="flex items-center space-x-2">
    <Input
      type="text"
      placeholder="Search the knowledge graph..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onKeyPress={(e) => e.key === "Enter" && onSend()}
    />
    <Button onClick={onSend}>
      <Send className="h-4 w-4" />
      <span className="sr-only">Send</span>
    </Button>
  </div>
);
