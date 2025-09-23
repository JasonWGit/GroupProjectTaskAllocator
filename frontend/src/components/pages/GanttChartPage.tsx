import { useEffect, useRef, useState } from "react";
import { DataSet } from "vis-data/peer";
import { Timeline, type TimelineOptions } from "vis-timeline/peer";
import "vis-timeline/styles/vis-timeline-graph2d.min.css";
import fetchFromBackend from "../../helperFunctions";
import { Box, Typography } from "@mui/material";
import moment from "moment";

type BackendTask = {
  id: string;
  name: string;
  start: string;
  end: string;
  progress?: number;
  dependencies?: string;
  custom_class?: string | null;
  worker_id: string;
  worker_name: string;
};

type WorkerInfo = {
  worker_id: string;
  worker_name: string;
  colour: string;
}

const COLOURS = [
    "#66c2a5",
    "#fc8d62",
    "#8da0cb",
    "#e78ac3",
    "#a6d854",
    "#ffd92f",
    "#e5c494",
    "#b3b3b3",
  ];

function fnv1a64(str: string): bigint {
  // FNV-1a 64-bit parameters
  const FNV_OFFSET = BigInt("0xcbf29ce484222325");
  const FNV_PRIME = BigInt("0x100000001b3");

  let hash = FNV_OFFSET;
  for (let i = 0; i < str.length; i++) {
    const code = BigInt(str.charCodeAt(i) & 0xff);
    hash = hash ^ code;
    hash = BigInt.asUintN(64, hash * FNV_PRIME);
  }
  return BigInt.asUintN(64, hash);
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  s /= 100;
  l /= 100;
  const k = (n: number) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) => {
    const x = l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    return Math.round(255 * x);
  };
  return [f(0), f(8), f(4)];
}
function rgbToHex(r: number, g: number, b: number) {
  return "#" + [r, g, b].map((x) => x.toString(16).padStart(2, "0")).join("");
}

// auto generate colour palette
function generatePalette(n: number, saturation = 65, lightness = 55): string[] {
  const GOLDEN_ANGLE = 137.50776405003785;
  const palette: string[] = [];
  for (let i = 0; i < n; i++) {
    const hue = (i * GOLDEN_ANGLE) % 360;
    const [r, g, b] = hslToRgb(hue, saturation, lightness);
    palette.push(rgbToHex(r, g, b));
  }
  return palette;
}

function assignWorkerColours(workerIds: string[], paletteSize = 256): Map<string, string> {
  // generate palette of requested size (cap reasonably)
  const size = Math.max(32, Math.min(paletteSize, 4096));
  const palette = generatePalette(size);

  const used = new Array<boolean>(size).fill(false);
  const map = new Map<string, string>();

  for (const id of workerIds) {
    // hash -> index
    const h = fnv1a64(id);
    let idx = Number(h % BigInt(size));
    // linear probing if collision
    let tries = 0;
    while (used[idx]) {
      idx = (idx + 1) % size;
      if (++tries > size) {
        // should never happen unless palette exhausted
        break;
      }
    }
    used[idx] = true;
    map.set(id, palette[idx]);
  }

  return map;
}

export default function GanttChartPage() {
  const [tasks, setTasks] = useState<BackendTask[]>([]);
    const [workerInfoMap, setWorkerInfoMap] = useState<Map<string, WorkerInfo>>(new Map());
  const containerRef = useRef<HTMLDivElement | null>(null);
  const timelineRef = useRef<Timeline | null>(null);
  const itemsRef = useRef<DataSet<any> | null>(null);

  // fetch tasks
  useEffect(() => {
    (async () => {
      const data = await fetchFromBackend("/get_gantt_chart_json/greedy", "GET");
      if (Array.isArray(data)) {
        setTasks(data);
        const workerIds = Array.from(new Set(data.map((t: any) => t.worker_id)));

        // choose palette size: scale with number of workers so collisions unlikely
        const paletteSize = Math.max(64, workerIds.length * 4); // e.g. 4x workers, min 64
        const colourMap = assignWorkerColours(workerIds, paletteSize);

        // build workerInfoMap
        const workerInfoMap = new Map<string, WorkerInfo>();
        workerIds.forEach((wId) => {
          // find worker_name from first matching task
          const found = data.find((d: any) => d.worker_id === wId);
          workerInfoMap.set(wId, {
            worker_id: wId,
            worker_name: found?.worker_name ?? wId,
            colour: colourMap.get(wId)!,
          });
        });
        setWorkerInfoMap(workerInfoMap);
      }

      
    })();
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    if (!tasks || tasks.length === 0) {
      if (timelineRef.current) {
        timelineRef.current.setItems(new DataSet([]));
      }
      return;
    }

    const itemsArray = tasks.map((t) => ({
      id: t.id,
      content: t.name,
      start: t.start,
      end: t.end,
      title: `${t.name}\n${t.start} → ${t.end}`,
      style: `background-color: ${workerInfoMap.get(t.worker_id)?.colour || "#ccc"}; 
              border-color: ${workerInfoMap.get(t.worker_id)?.colour || "#ccc"}; 
              color: black;`,
    }));

    if (!itemsRef.current) itemsRef.current = new DataSet(itemsArray);
    else {
      itemsRef.current.clear();
      itemsRef.current.add(itemsArray);
    }

    const startTimes = tasks.map((t) => new Date(t.start).getTime());
    const endTimes = tasks.map((t) => new Date(t.end).getTime());
    const minStartMs = Math.min(...startTimes);
    const maxEndMs = Math.max(...endTimes);

    const PAD_MS = 15 * 60 * 1000;

    const dayStart = new Date(minStartMs);
    dayStart.setHours(0, 0, 0, 0); // midnight of earliest task's day

    const windowEnd = new Date(maxEndMs + PAD_MS);

    const taskSpanMs = Math.max(1, maxEndMs - minStartMs);
    const MAX_INITIAL_WINDOW_MS = 6 * 60 * 60 * 1000; // 6 hours
    const initialWindowMs = Math.min(taskSpanMs + 2 * PAD_MS, MAX_INITIAL_WINDOW_MS);

    const INITIAL_LEFT_MARGIN_MS = 60 * 60 * 1000; // 1 hour after midnight

    let initialStart = new Date(Math.max(dayStart.getTime() + INITIAL_LEFT_MARGIN_MS, minStartMs - PAD_MS));

    if (initialStart.getTime() + initialWindowMs > windowEnd.getTime()) {
      initialStart = new Date(windowEnd.getTime() - initialWindowMs);
      if (initialStart.getTime() < dayStart.getTime()) {
        initialStart = new Date(dayStart.getTime());
      }
    }
    const initialEnd = new Date(initialStart.getTime() + initialWindowMs);

    const options: TimelineOptions = {
      stack: true,
      horizontalScroll: true,
      zoomable: true,
      orientation: "top",
      zoomKey: "ctrlKey" as const,
      zoomMin: 1000 * 30,               // 1 minute
      zoomMax: 1000 * 60 * 60 * 48,     // 1 day
      showCurrentTime: false,           // hide red line
      min: dayStart,                    // disable scrolling before start of first task
      // scrolling is enabled past last task
      start: initialStart,              // initial view (slightly after midnight)
      end: initialEnd,
      timeAxis: { 
        scale: "hour", 
        step: 1,
      }, // show hours, no "Day" header
      format: {
        minorLabels: function(date: Date) {
          return moment(date).format("H"); // just hours, no ":00"
        },
        ////// USE majorLabels to change the thing at the top left of the gantt chart which reads "Mon 22 September"
        // majorLabels: function(date: Date) {
        //   return moment(date).format("D"); 
        // }
      },
      template: (item: any) => {
        const short =
          typeof item.content === "string" && item.content.length > 30
            ? item.content.slice(0, 27) + "..."
            : item.content;
        return `<div style="padding:4px; font-size:12px; white-space:nowrap">${short}</div>`;
      },
    };

    if (timelineRef.current) {
      timelineRef.current.setItems(itemsRef.current!);
      timelineRef.current.setOptions(options);
      timelineRef.current.setWindow(initialStart, initialEnd);
    } else {
      timelineRef.current = new Timeline(containerRef.current, itemsRef.current, options);
      timelineRef.current.setWindow(initialStart, initialEnd);
    }

    return () => {
      if (timelineRef.current) {
        timelineRef.current.destroy();
        timelineRef.current = null;
      }
    };
  }, [tasks, workerInfoMap]);

  return (
    <>
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%", px: 10, pt: 3 }}>
        <Typography variant="h4" sx={{ mb: 3}}>Project Gantt Chart</Typography>
        <div ref={containerRef} style={{ width: "100%" }} />
        {/* Legend */}
        <Box sx={{ mt: 2, display: "flex", gap: 2, flexWrap: "wrap" }}>
          {Array.from(workerInfoMap.entries()).map(([workerId, workerInfo]) => (
            <Box key={workerId} sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <div style={{ width: 20, height: 20, backgroundColor: workerInfo.colour, border: "1px solid black" }} />
              <span>{workerInfo.worker_name}</span>
            </Box>
          ))}
        </Box>
      </Box>
      
    </>
  );
}
