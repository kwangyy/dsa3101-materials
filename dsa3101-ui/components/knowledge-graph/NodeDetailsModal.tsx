import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

interface NodeDetailsModalProps {
  node: {
    id: string;
    details?: {
      [key: string]: any;
    };
  } | null;
  onClose: () => void;
}

export const NodeDetailsModal = ({ node, onClose }: NodeDetailsModalProps) => {
  if (!node) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-background rounded-lg p-6 max-w-md w-full max-h-[80vh]">
        <h2 className="text-xl font-semibold mb-4">{node.id}</h2>
        <ScrollArea className="h-[300px]">
          {node.details ? (
            <div className="space-y-2">
              {Object.entries(node.details).map(([key, value]) => (
                <div key={key} className="border-b pb-2">
                  <span className="font-medium">{key}: </span>
                  <span>{value}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">No additional details available</p>
          )}
        </ScrollArea>
        <div className="mt-4 flex justify-end">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </div>
  );
};
