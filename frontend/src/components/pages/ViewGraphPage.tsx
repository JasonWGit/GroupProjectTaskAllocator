import { useEffect, useRef, useState } from "react";
import fetchFromBackend from "../../helperFunctions"
import { Box } from "@mui/material";
import { Network, DataSet } from "vis-network/standalone";

type Node = { 
  id: string; 
  label: string 
};

type Edge = { 
  from: string; 
  to: string;
};

type GraphJSON = {
  nodes: Node[];
  edges: Edge[];
};

export default function ViewGraphPage() {
  const [graphJSON, setGraphJSON] = useState<GraphJSON | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // get the JSON formatted graph for vis.js from the backend
  const fetchFormattedGraph = async () => {
    const response = await fetchFromBackend("/get_graph_formatted_json", "GET");

    setGraphJSON(response);
  }

  useEffect(() => {
    fetchFormattedGraph();
  }, [])

  useEffect(() => {
    if (graphJSON && containerRef.current) {
      const nodes = new DataSet<Node>(graphJSON.nodes);
      const edges = new DataSet<any>(graphJSON.edges);

      const options = {
        layout: { hierarchical: { direction: "UD", sortMethod: "directed" } },
        edges: { arrows: { to: true } },
        nodes: { shape: "box" },
      };

      const data = {
        nodes: nodes,
        edges: edges
      };

      new Network(containerRef.current, data, options);
    }
  }, [graphJSON]);

  return (
    <>
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div ref={containerRef} style={{ height: "600px", width: "100%" }} />
      </Box>
    </>
  )
}