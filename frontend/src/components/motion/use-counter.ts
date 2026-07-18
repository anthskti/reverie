"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Animates a number from 0 to `end` once the element scrolls into view.
 * Mirrors new-design's landing page stat counters.
 */
export function useCounter(end: number, duration = 1800) {
  const [count, setCount] = useState(0);
  const [started, setStarted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setStarted(true);
      },
      { threshold: 0.3 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!started) return;
    const steps = 60;
    const stepVal = end / steps;
    let current = 0;
    const id = setInterval(() => {
      current += stepVal;
      if (current >= end) {
        setCount(end);
        clearInterval(id);
      } else {
        setCount(current);
      }
    }, duration / steps);
    return () => clearInterval(id);
  }, [started, end, duration]);

  return { count, ref };
}
