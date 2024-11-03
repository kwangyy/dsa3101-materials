import React from 'react';

interface StatisticsProps {
  metrics?: {
    accuracy?: number;
    completeness_score?: number;
    consistency_score?: number;
    overall_score?: number;
    valid_count?: number;
    invalid_count?: number;
    invalid_cases?: string[];
  };
  graphData?: {
    nodes: any[];
    links: any[];
  };
}

export const Statistics: React.FC<StatisticsProps> = ({ metrics, graphData }) => (
  <div className="bg-muted p-4 rounded-lg">
    <h3 className="font-semibold mb-4">Statistics</h3>
    
    {/* Main Grid Container */}
    <div className="grid grid-cols-2 gap-4">
      {/* Left Column */}
      <div className="space-y-2">
        <div>
          <h4 className="font-medium text-muted-foreground text-sm">Structure</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>Nodes: {graphData?.nodes?.length || 0}</div>
            <div>Edges: {graphData?.links?.length || 0}</div>
          </div>
        </div>

        <div>
          <h4 className="font-medium text-muted-foreground text-sm">Scores</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>Accuracy: {(metrics?.accuracy || 0).toFixed(2)}%</div>
            <div>Overall: {(metrics?.overall_score || 0).toFixed(2)}</div>
          </div>
        </div>
      </div>

      {/* Right Column */}
      <div className="space-y-2">
        <div>
          <h4 className="font-medium text-muted-foreground text-sm">Quality</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>Complete: {(metrics?.completeness_score || 0).toFixed(2)}</div>
            <div>Consistent: {(metrics?.consistency_score || 0).toFixed(2)}</div>
          </div>
        </div>

        <div>
          <h4 className="font-medium text-muted-foreground text-sm">Relations</h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>Valid: {metrics?.valid_count || 0}</div>
            <div>Invalid: {metrics?.invalid_count || 0}</div>
          </div>
        </div>
      </div>
    </div>

    {/* Invalid Cases - Full Width */}
    {metrics?.invalid_cases && metrics.invalid_cases.length > 0 && (
      <div className="mt-4">
        <h4 className="font-medium text-muted-foreground text-sm mb-1">Invalid Cases</h4>
        <div className="max-h-20 overflow-y-auto">
          <ul className="space-y-1 text-xs text-red-500">
            {metrics.invalid_cases.map((invalidCase, index) => (
              <li key={index}>{invalidCase}</li>
            ))}
          </ul>
        </div>
      </div>
    )}
  </div>
);
