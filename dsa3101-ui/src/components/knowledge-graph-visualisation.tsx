"use client"

import React, { useEffect, useRef } from 'react';
import { Network, Options } from 'vis-network';
import { DataSet } from 'vis-data';

interface KnowledgeGraphProps {
  data: {
    nodes: Array<{ id: number; label: string }>;
    edges: Array<{ from: number; to: number }>;
  };
}

export function KnowledgeGraphVisualization({ data }: KnowledgeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      const nodes = new DataSet(data.nodes);
      const edges = new DataSet(data.edges);

      const options: Options = {
        nodes: {
          shape: 'dot',
          size: 16,
          font: {
            size: 12,
            color: '#ffffff'
          },
          borderWidth: 2
        },
        edges: {
          width: 1,
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
      };

      networkRef.current = new Network(containerRef.current, { nodes, edges }, options);

      return () => {
        if (networkRef.current) {
          networkRef.current.destroy();
          networkRef.current = null;
        }
      };
    }
  }, []);

  useEffect(() => {
    if (networkRef.current) {
      networkRef.current.setData({
        nodes: new DataSet(data.nodes),
        edges: new DataSet(data.edges)
      });
    }
  }, [data]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
}