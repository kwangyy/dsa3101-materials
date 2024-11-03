import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface OntologySelectionProps {
  onCustomUpload: (file: File) => void;
  onGenerateOntology: () => void;
}

export const OntologySelection = ({ onCustomUpload, onGenerateOntology }: OntologySelectionProps) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white p-6 rounded-lg">
      <h2 className="text-xl font-bold mb-4">Select Ontology</h2>
      <Input
        type="file"
        accept=".json"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file && file.name.endsWith('.json')) {
            onCustomUpload(file);
          } else {
            alert('Please upload a .json file.');
          }
        }}
        className="hidden"
        id="ontology-file-upload"
      />
      <div className="flex flex-col space-y-4">
        <div className="flex space-x-2">
          <Button onClick={() => document.getElementById('ontology-file-upload')?.click()} className="flex-1">
            Upload Custom Ontology
          </Button>
          <Button onClick={onGenerateOntology} className="flex-1">
            Use LLM-Generated Ontology
          </Button>
        </div>
      </div>
    </div>
  </div>
)
