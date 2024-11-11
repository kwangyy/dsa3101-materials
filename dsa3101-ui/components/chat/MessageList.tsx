import { Message } from "./Message"
import { Message as MessageType } from "@/types/chat"

interface MessageListProps {
  messages: MessageType[];
}

export const MessageList = ({ messages }: MessageListProps) => (
  <div className="space-y-4">
    {messages.map((message, index) => (
      <Message key={index} role={message.role} content={message.content} />
    ))}
  </div>
);
