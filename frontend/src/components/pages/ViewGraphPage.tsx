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
        layout: {
          hierarchical: {
            direction: "LR",
            sortMethod: "directed",
            nodeSpacing: 200,
            levelSeparation: 150
          }
        },
        physics: false,
        edges: {
          arrows: { to: { enabled: true, scaleFactor: 0.8 } },
          smooth: true,
          color: { color: "#888" }
        },
        nodes: {
          shape: "box",
          color: {
            background: "#f0f4ff",
            border: "#3f51b5",
            highlight: { background: "#c5cae9", border: "#303f9f" }
          },
          font: {
            size: 16,
            color: "#333"
          },
          margin: { top: 10, right: 10, bottom: 10, left: 10 },
          widthConstraint: { minimum: 100, maximum: 200 }
        },
        interaction: {
          dragNodes: false,
          dragView: false,
          zoomView: false
        }
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