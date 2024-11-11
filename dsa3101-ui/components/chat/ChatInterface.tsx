import { Separator } from "@/components/ui/separator"
import { MessageList } from "./MessageList"
import { MessageInput } from "./MessageInput"
import { Statistics } from "./Statistics"
import { ChatInterfaceProps } from "@/types/chat"

export const ChatInterface = ({ messages, input, onInputChange, onSend }: ChatInterfaceProps) => (
  <div className="flex flex-col" style={{ height: "calc(100% - 200px)" }}>
    <h2 className="text-lg font-semibold p-4 shrink-0">Search Interface</h2>
    
    {/* Message container with reduced height */}
    <div className="overflow-y-auto flex-grow" style={{ maxHeight: "400px" }}>
      <div className="p-4">
        <MessageList messages={messages} />
      </div>
    </div>
    
    {/* Input container fixed at bottom */}
    <div className="p-4 border-t mt-auto shrink-0">
      <MessageInput
        value={input}
        onChange={onInputChange}
        onSend={onSend}
      />
    </div>
  </div>
)
