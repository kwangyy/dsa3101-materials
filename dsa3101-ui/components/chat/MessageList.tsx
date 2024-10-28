import { ScrollArea } from "@/components/ui/scroll-area"
import { Message } from "./Message"
import { Message as MessageType } from "@/types/chat"

interface MessageListProps {
  messages: MessageType[];
}

export const MessageList = ({ messages }: MessageListProps) => (
  <ScrollArea className="flex-1 pr-4">
    {messages.map((message, index) => (
      <Message key={index} role={message.role} content={message.content} />
    ))}
  </ScrollArea>
);
