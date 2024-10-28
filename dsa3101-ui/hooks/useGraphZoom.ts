import { useRef } from 'react';
import * as d3 from 'd3';

export const useGraphZoom = (svgRef: React.RefObject<SVGSVGElement>) => {
  const zoomRef = useRef<any>(null);
  
  const handleZoom = (factor: number) => {
    if (!svgRef.current || !zoomRef.current) return;
    
    const svg = d3.select(svgRef.current);
    svg.transition().duration(300).call(
      zoomRef.current.scaleBy, factor
    );
  };

  return { zoomRef, handleZoom };
};
