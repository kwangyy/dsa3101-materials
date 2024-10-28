import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Button } from "@/components/ui/button";
import { Plus, Minus } from 'lucide-react';

interface Node {
  id: string;
}

interface Link {
  source: string;  // Changed from head_node
  target: string;  // Changed from tail_node
  relationship: string;
}

interface KnowledgeGraphProps {
  nodes: Node[];
  links: Link[];
  onUploadClick: () => void;
  data: any;
  name: string;
}

const KnowledgeGraphD3: React.FC<KnowledgeGraphProps> = ({ nodes, links, onUploadClick, data, name }) => {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const zoomRef = useRef<any>(null); // Add this line
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [currentZoom, setCurrentZoom] = useState(1);

  useEffect(() => {
    if (!containerRef.current) return;

    const updateDimensions = () => {
      const container = containerRef.current;
      if (container) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        setDimensions({ width, height });
      }
    };

    updateDimensions();
    const resizeObserver = new ResizeObserver(updateDimensions);
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // Add zoom behavior
  useEffect(() => {
    if (!svgRef.current || !nodes || !links) return;

    // Clear any existing SVG content
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    
    const g = svg.append('g');

    // Store zoom behavior in ref
    zoomRef.current = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        setCurrentZoom(event.transform.k);
      });

    svg.call(zoomRef.current as any);

    // Modify the D3 visualization effect
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(200)) // Increased distance
      .force('charge', d3.forceManyBody().strength(-2000)) // Much stronger repulsion
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2))
      .force('x', d3.forceX(dimensions.width / 2).strength(0.1))
      .force('y', d3.forceY(dimensions.height / 2).strength(0.1));

    const link = g.append('g')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke-width', 1.5);

    // Create node groups
    const nodeGroup = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g');

    // Larger background circle for better visibility
    nodeGroup.append('circle')
      .attr('r', 30)
      .attr('fill', 'white')
      .attr('stroke', '#69b3a2')
      .attr('stroke-width', 2);

    // Main circle
    nodeGroup.append('circle')
      .attr('r', 30)
      .attr('fill', '#69b3a2')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Larger, more visible text
    nodeGroup.append('text')
      .text((d: any) => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('font-size', '14px')
      .attr('fill', 'black') // Changed from 'white' to 'black'
      .attr('font-weight', 'bold');

    // Apply drag behavior to the whole group
    nodeGroup.call(drag(simulation));

    // Add relationship labels
    const linkText = g.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .text(d => d.relationship)
      .attr('font-size', '8px')
      .attr('text-anchor', 'middle')
      .attr('dy', -5);

    simulation.on('tick', () => {
      // Update node groups position
      nodeGroup
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);

      // Update links
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      // Update link labels
      linkText
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);
    });

    function drag(simulation: any) {
      function dragstarted(event: any, d: any) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(event: any, d: any) {
        d.fx = event.x;
        d.fy = event.y;
      }

      function dragended(event: any, d: any) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }

      return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }
  }, [nodes, links, dimensions]);

  // Update zoom controls
  const handleZoom = (factor: number) => {
    if (!svgRef.current || !zoomRef.current) return;
    
    const svg = d3.select(svgRef.current);
    svg.transition().duration(300).call(
      zoomRef.current.scaleBy, factor
    );
  };

  if (!nodes || nodes.length === 0) {
    return (
      <div className="w-full h-full bg-muted rounded-lg flex flex-col items-center justify-center p-4">
        <Button onClick={onUploadClick}>Upload</Button>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="w-full h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <p className="text-muted-foreground">Knowledge Graph: {name}</p>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => handleZoom(1.2)}
          >
            <Plus className="h-4 w-4" />
          </Button>
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => handleZoom(0.8)}
          >
            <Minus className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <div className="flex-1 border-2 border-gray-200 rounded-lg">
        <svg 
          ref={svgRef} 
          style={{ width: '100%', height: '100%' }}
        />
      </div>
    </div>
  );
};

export default KnowledgeGraphD3;
