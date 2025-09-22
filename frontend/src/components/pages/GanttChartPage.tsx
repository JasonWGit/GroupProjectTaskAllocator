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
};

export default function GanttChartPage() {
  const [tasks, setTasks] = useState<BackendTask[]>([]);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const timelineRef = useRef<Timeline | null>(null);
  const itemsRef = useRef<DataSet<any> | null>(null);

  // fetch tasks
  useEffect(() => {
    (async () => {
      const data = await fetchFromBackend("/get_gantt_chart_json/dp", "GET");
      if (Array.isArray(data)) setTasks(data);
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
  }, [tasks]);

  return (
    <>
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%", px: 10, pt: 3 }}>
        <Typography variant="h4" sx={{ mb: 3}}>Project Gantt Chart</Typography>
        <div ref={containerRef} style={{ width: "100%" }} />
      </Box>
    </>
  );
}
