import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File) => void;
}

export const UploadModal = ({ isOpen, onClose, onUpload }: UploadModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Upload Data</h2>
        <Input
          type="file"
          accept=".txt"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file && file.name.endsWith('.txt')) {
              onUpload(file);
              onClose();
            } else {
              alert('Please upload a .txt file');
            }
          }}
          className="hidden"
          id="file-upload"
        />
        <div className="mt-4 flex justify-end">
          <Button onClick={onClose} variant="outline" className="mr-2">Cancel</Button>
          <Button onClick={() => document.getElementById('file-upload')?.click()} variant="outline">Select File</Button>
        </div>
      </div>
    </div>
  )
}
