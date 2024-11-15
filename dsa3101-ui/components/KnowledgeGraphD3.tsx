import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Button } from "@/components/ui/button";
import { Plus, Minus } from 'lucide-react';
import { NodeDetailsModal } from './knowledge-graph/NodeDetailsModal';
import { computeCosineSimilarity } from '@/lib/similarity';

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
  isLoading?: boolean;
}

// Add cache at the top of your component
const wikiCache = new Map<string, { title: string | null, timestamp: number }>();
const CACHE_DURATION = 1000 * 60 * 60; // 1 hour cache

// Optimized Wikipedia fetch function
const fetchWikipediaData = async (searchTerm: string) => {
  // Check cache first
  const now = Date.now();
  const cached = wikiCache.get(searchTerm);
  if (cached && (now - cached.timestamp < CACHE_DURATION)) {
    return cached.title ? { title: cached.title } : null;
  }

  try {
    const searchUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(searchTerm)}&format=json&origin=*&srlimit=5`;
    const searchResponse = await fetch(searchUrl);
    const searchData = await searchResponse.json();

    if (!searchData.query.search.length) {
      wikiCache.set(searchTerm, { title: null, timestamp: now });
      return null;
    }

    // Process results
    const topResults = searchData.query.search;
    const similarities = topResults.map((result: any) => ({
      ...result,
      similarity: computeCosineSimilarity(
        searchTerm.toLowerCase(),
        result.title.toLowerCase()
      )
    }));

    const goodMatches = similarities.filter(result => result.similarity > 0.95);
    if (!goodMatches.length) {
      wikiCache.set(searchTerm, { title: null, timestamp: now });
      return null;
    }

    const bestMatch = goodMatches[0];
    wikiCache.set(searchTerm, { title: bestMatch.title, timestamp: now });
    return { title: bestMatch.title };
  } catch (error) {
    console.error('Error fetching Wikipedia data:', error);
    return null;
  }
};

const KnowledgeGraphD3: React.FC<KnowledgeGraphProps> = ({ nodes, links, onUploadClick, data, name, isLoading }) => {
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

    // Define arrow marker
    const defs = svg.append('defs');
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 32)
      .attr('refY', 0)
      .attr('markerWidth', 10)
      .attr('markerHeight', 10)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Create the force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(150))  // Increased distance
      .force('charge', d3.forceManyBody().strength(-500))  // Stronger repulsion
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2))
      .force('collision', d3.forceCollide().radius(60));  // Increased collision radius

    // Create links with arrows
    const l = g.append('g')
      .selectAll('path')
      .data(links)
      .join('path')
      .attr('stroke', '#999')
      .attr('stroke-width', 1.5)
      .attr('fill', 'none')
      .attr('marker-end', 'url(#arrowhead)');

    // Create link labels
    const linkText = g.append('g')
      .selectAll('text')
      .data(links)
      .join('text')
      .attr('font-size', '10px')
      .attr('fill', '#666')
      .text((d: any) => d.relationship);

    // Create nodes group
    const nodeGroup = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node');

    // Add circles to nodes
    nodeGroup.append('circle')
      .attr('r', 30)
      .attr('fill', '#69b3a2');

    // Add labels to nodes
    nodeGroup.append('text')
      .text((d: any) => d.id)
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .attr('font-size', '12px')
      .attr('fill', 'black')
      .attr('font-weight', 'bold')
      .each(function(d: any) {  // Handle long text
        const text = d3.select(this);
        const words = d.id.split(/\s+/);
        if (words.length > 2) {
          text.text('');
          text.append('tspan')
            .attr('x', 0)
            .attr('dy', '-0.5em')
            .text(words.slice(0, 2).join(' '));
          text.append('tspan')
            .attr('x', 0)
            .attr('dy', '1.2em')
            .text(words.slice(2).join(' '));
        }
      });

    // Define and add drag behavior
    const drag = d3.drag<SVGGElement, any>()
      .on('start', (event) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        const d = event.subject;
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event) => {
        const d = event.subject;
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event) => {
        if (!event.active) simulation.alphaTarget(0);
        const d = event.subject;
        d.fx = null;
        d.fy = null;
      });

    // Apply drag to nodes
    nodeGroup.call(drag as any);

    // Update positions on each tick
    simulation.on('tick', () => {
      // Update node positions
      nodeGroup.attr('transform', (d: any) => `translate(${d.x},${d.y})`);

      // Update link positions with arrows
      l.attr('d', (d: any) => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy);
        const endPointRatio = (dr - 32) / dr;
        const endX = d.source.x + dx * endPointRatio;
        const endY = d.source.y + dy * endPointRatio;
        return `M${d.source.x},${d.source.y}L${endX},${endY}`;
      });

      // Update link label positions
      linkText
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2 - 5);

      // Update info box positions
      infoBoxContainer.selectAll('.info-box')
        .attr('transform', function() {
          const node = d3.select(this).datum() as any;
          return `translate(${node.x},${node.y})`;
        });
    });

    // Create a separate group for info boxes at the top level
    const infoBoxContainer = g.append('g')
      .attr('class', 'info-box-container');

    // Add click handler for nodes
    nodeGroup.on('click', async function(event, d: any) {
      event.stopPropagation();
      
      // Check if clicking the same node
      const existingBox = infoBoxContainer.selectAll('.info-box').filter(function(data: any) {
        return data.id === d.id;
      });
      
      // If info box exists for this node, remove it and return
      if (!existingBox.empty()) {
        existingBox.remove();
        return;
      }
      
      // Remove any other existing info boxes
      infoBoxContainer.selectAll('*').remove();
      
      // Create new info box
      const infoBox = infoBoxContainer.append('g')
        .attr('class', 'info-box')
        .datum(d)
        .attr('transform', `translate(${d.x},${d.y})`);

      // Add background rect first
      const rect = infoBox.append('rect')
        .attr('x', -70)
        .attr('y', 35)
        .attr('width', 140)
        .attr('height', 95)
        .attr('fill', 'white')
        .attr('stroke', '#69b3a2')
        .attr('stroke-width', 1)
        .attr('rx', 5);

      // Add text content
      const text = infoBox.append('text')
        .attr('text-anchor', 'middle')
        .attr('y', 55)
        .attr('font-size', '11px')
        .attr('fill', 'black');

      // Add immediate content
      text.append('tspan')
        .attr('x', 0)
        .attr('dy', 0)
        .text(`Type: ${d.details?.type || 'Entity'}`);
      
      text.append('tspan')
        .attr('x', 0)
        .attr('dy', '1.2em')
        .text(`Connections: ${d.details?.connections || 0}`);

      // Add relationships with line wrapping
      const relationships = d.details?.relationships || [];
      const uniqueRelationships = [...new Set(relationships)];
      const relationText = `Relations: ${uniqueRelationships.join(', ')}`;
      const words = relationText.split(' ');
      let line = '';
      let lineCount = 2;

      words.forEach(word => {
        const testLine = line + word + ' ';
        if (testLine.length > 25) {
          text.append('tspan')
            .attr('x', 0)
            .attr('dy', '1.2em')
            .text(line);
          line = word + ' ';
          lineCount++;
        } else {
          line = testLine;
        }
      });
      if (line) {
        text.append('tspan')
          .attr('x', 0)
          .attr('dy', '1.2em')
          .text(line);
      }

      // Add placeholder for Wikipedia link with loading state
      const linkTspan = text.append('tspan')
        .attr('x', 0)
        .attr('dy', '1.5em')
        .attr('fill', '#999')
        .text('Checking Wikipedia...');

      // Fetch Wikipedia data in parallel
      fetchWikipediaData(d.id).then(wikiData => {
        if (wikiData) {
          linkTspan
            .attr('class', 'wiki-link')
            .attr('fill', '#2563eb')
            .attr('text-decoration', 'underline')
            .attr('cursor', 'pointer')
            .text('Learn More')
            .on('click', (e) => {
              e.stopPropagation();
              window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(wikiData.title)}`, '_blank');
            });
        } else {
          linkTspan.remove();
        }

        // Adjust box size after Wikipedia check
        const textBox = (text.node() as SVGTextElement).getBBox();
        const padding = { x: 20, y: 15 };
        const boxWidth = Math.max(140, textBox.width + (padding.x * 2));
        const boxHeight = textBox.height + (padding.y * 2);

        rect.attr('x', -boxWidth/2)
            .attr('width', boxWidth)
            .attr('height', boxHeight);
      });
    });

    // Add click handler to svg to close info boxes
    svg.on('click', () => {
      infoBoxContainer.selectAll('*').remove();
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

  if (isLoading) {
    return (
      <div className="w-full h-full bg-muted rounded-lg flex flex-col items-center justify-center p-4 gap-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p className="text-muted-foreground">Your knowledge graph is loading...</p>
      </div>
    );
  }

  if (!nodes?.length && !links?.length && !isLoading) {
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
