"use client"

import React, { useEffect, useRef } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';

interface KnowledgeGraphProps {
  data: {
    nodes: Array<{ id: number; label: string }>;
    edges: Array<{ from: number; to: number }>;
  };
}

export function KnowledgeGraphVisualization({ data }: KnowledgeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      const nodes = new DataSet(data.nodes);
      const edges = new DataSet(data.edges);

      const network = new Network(containerRef.current, { nodes, edges }, {
        nodes: {
          shape: 'dot',
          size: 16,
        },
        physics: {
          forceAtlas2Based: {
            gravitationalConstant: -26,
            centralGravity: 0.005,
            springLength: 230,
            springConstant: 0.18,
          },
          maxVelocity: 146,
          solver: 'forceAtlas2Based',
          timestep: 0.35,
          stabilization: { iterations: 150 },
        },
      });

      return () => {
        network.destroy();
      };
    }
  }, [data]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
}