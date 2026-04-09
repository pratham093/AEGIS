"use client";
import { useEffect, useRef } from "react";

export default function DotGrid() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: -1000, y: -1000 });
  const smoothRef = useRef({ x: -1000, y: -1000 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    const spacing = 18;
    const radius = 1.0;
    const glowRadius = 250;
    const friction = 0.08;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const onMouse = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    window.addEventListener("mousemove", onMouse);

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      smoothRef.current.x += (mouseRef.current.x - smoothRef.current.x) * friction;
      smoothRef.current.y += (mouseRef.current.y - smoothRef.current.y) * friction;

      const mx = smoothRef.current.x;
      const my = smoothRef.current.y;

      for (let x = spacing; x < canvas.width; x += spacing) {
        for (let y = spacing; y < canvas.height; y += spacing) {
          const dx = x - mx;
          const dy = y - my;
          const dist = Math.sqrt(dx * dx + dy * dy);

          const proximity = Math.max(0, 1 - dist / glowRadius);

          const pushStrength = proximity * proximity * 18;
          const angle = Math.atan2(dy, dx);
          const drawX = x + Math.cos(angle) * pushStrength;
          const drawY = y + Math.sin(angle) * pushStrength;

          const dotRadius = radius + proximity * 3;
          const opacity = 0.12 + proximity * 0.6;

          const r = Math.round(34 * proximity);
          const g = Math.round(120 + proximity * 137);
          const b = Math.round(60 + proximity * 34);

          ctx.beginPath();
          ctx.arc(drawX, drawY, dotRadius, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${opacity})`;
          ctx.fill();
        }
      }

      animId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", onMouse);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ opacity: 0.7 }}
    />
  );
}
