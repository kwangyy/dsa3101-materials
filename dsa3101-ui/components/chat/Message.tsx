import { MessageProps } from "@/types/chat";

export const Message = ({ role, content }: MessageProps) => (
  <div className={`mb-4 ${role === "user" ? "text-right" : "text-left"}`}>
    <span
      className={`inline-block p-2 rounded-lg ${
        role === "user"
          ? "bg-primary text-primary-foreground"
          : "bg-muted"
      }`}
    >
      {content}
    </span>
  </div>
);
