export interface Message {
  role: string;
  content: string;
}

export interface MessageProps {
  role: string;
  content: string;
}

export interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
}

export interface ChatInterfaceProps {
  messages: Message[];
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
}
