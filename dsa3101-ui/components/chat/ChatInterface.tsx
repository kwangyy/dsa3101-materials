import { Separator } from "@/components/ui/separator"
import { MessageList } from "./MessageList"
import { MessageInput } from "./MessageInput"
import { Statistics } from "./Statistics"
import { ChatInterfaceProps } from "@/types/chat"

export const ChatInterface = ({ messages, input, onInputChange, onSend }: ChatInterfaceProps) => (
  <div className="flex flex-col h-full">
    <div className="flex-1 p-4 flex flex-col">
      <h2 className="text-lg font-semibold mb-4">Search Interface</h2>
      <MessageList messages={messages} />
      <Separator className="my-4" />
      <MessageInput
        value={input}
        onChange={onInputChange}
        onSend={onSend}
      />
    </div>
    <div className="p-4 border-t">
      <Statistics />
    </div>
  </div>
)
