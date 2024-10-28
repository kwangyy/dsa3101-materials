import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Button } from "@/components/ui/button";
import { Plus, Minus } from 'lucide-react';
import { NodeDetailsModal } from './knowledge-graph/NodeDetailsModal';

interface Node {
  id: string;
  details?: {
    [key: string]: any;
  };
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

// Define the drag behavior
const drag = (simulation: any) => {
  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event: any) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended);
};

const KnowledgeGraphD3: React.FC<KnowledgeGraphProps> = ({ nodes, links, onUploadClick, data, name }) => {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const zoomRef = useRef<any>(null); // Add this line
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [currentZoom, setCurrentZoom] = useState(1);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

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

    // Create links first (they should be behind nodes)
    const l = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 1);

    // Create link labels
    const linkText = g.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .text(d => d.relationship)
      .attr('font-size', '8px')
      .attr('text-anchor', 'middle')
      .attr('dy', -5);

    // Create node groups
    const nodeGroup = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g');

    // Add main circle for each node
    nodeGroup.append('circle')
      .attr('r', 30)
      .attr('fill', '#69b3a2')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add node labels
    nodeGroup.append('text')
      .text((d: any) => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('font-size', '14px')
      .attr('fill', 'black')  // Changed from 'white' to 'black'
      .attr('font-weight', 'bold');

    // Create info boxes (hidden by default)
    const infoBoxGroup = nodeGroup.append('g')
      .attr('class', 'info-box')
      .style('display', 'none');

    // Add info box background with increased height
    infoBoxGroup.append('rect')
      .attr('x', -60)
      .attr('y', 35)
      .attr('width', 120)
      .attr('height', 80)  // Increased height to accommodate wrapped text
      .attr('fill', 'white')
      .attr('stroke', '#69b3a2')
      .attr('stroke-width', 1)
      .attr('rx', 5);

    // Add info box content with text wrapping
    infoBoxGroup.append('text')
      .attr('text-anchor', 'middle')
      .attr('y', 55)
      .attr('font-size', '10px')
      .attr('fill', 'black')
      .each(function(d: any) {
        const text = d3.select(this);
        const maxWidth = 110; // Maximum width for text (less than box width)
        
        const relationships = d.details?.relationships || [];
        const uniqueRelationships = [...new Set(relationships)];
        
        // Helper function to wrap text
        function wrapText(text: string): string[] {
          const words = text.split(' ');
          const lines: string[] = [];
          let currentLine = '';
          
          words.forEach(word => {
            const testLine = currentLine ? `${currentLine} ${word}` : word;
            if (testLine.length * 6 < maxWidth) { // Approximate character width
              currentLine = testLine;
            } else {
              lines.push(currentLine);
              currentLine = word;
            }
          });
          if (currentLine) lines.push(currentLine);
          return lines;
        }

        // Add type
        text.append('tspan')
          .attr('x', 0)
          .attr('dy', 0)
          .text(`Type: ${d.details?.type || 'Entity'}`);
        
        // Add connections
        text.append('tspan')
          .attr('x', 0)
          .attr('dy', '1.2em')
          .text(`Connections: ${d.details?.connections || 0}`);
        
        // Add relationships with wrapping
        const relationText = `Relations: ${uniqueRelationships.join(', ')}`;
        const wrappedLines = wrapText(relationText);
        wrappedLines.forEach((line, i) => {
          text.append('tspan')
            .attr('x', 0)
            .attr('dy', i === 0 ? '1.2em' : '1.1em')
            .text(line);
        });
      });

    // Add click handlers
    nodeGroup.on('click', (event, d: any) => {
      event.stopPropagation();
      
      // Hide all info boxes first
      nodeGroup.select('.info-box').style('display', 'none');
      
      // Toggle the clicked node's info box
      const clickedInfoBox = d3.select(event.currentTarget).select('.info-box');
      const isCurrentlyVisible = clickedInfoBox.style('display') !== 'none';
      clickedInfoBox.style('display', isCurrentlyVisible ? 'none' : 'block');
    });

    // Add drag behavior
    nodeGroup.call(drag(simulation));

    // Click handler for svg to close info boxes
    svg.on('click', () => {
      nodeGroup.select('.info-box').style('display', 'none');
    });

    // Update simulation tick function
    simulation.on('tick', () => {
      // Update node positions
      nodeGroup
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);

      // Update link positions
      l.attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      // Update link label positions
      linkText
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2);
    });
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
      {selectedNode && (
        <NodeDetailsModal
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
};

export default KnowledgeGraphD3;
