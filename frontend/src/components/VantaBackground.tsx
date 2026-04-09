"use client";
import { useEffect, useRef, useState } from "react";

export default function VantaBackground() {
  const vantaRef = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [vantaEffect, setVantaEffect] = useState<any>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (vantaEffect) return;

    const id = requestIdleCallback ?? setTimeout;
    const handle = id(async () => {
      // @ts-expect-error - three has no declaration file
      const THREE = await import("three");
      // @ts-expect-error - vanta has no declaration file
      const NET = (await import("vanta/dist/vanta.net.min")).default;

      if (vantaRef.current) {
        const effect = NET({
          el: vantaRef.current,
          THREE,
          mouseControls: true,
          touchControls: false,
          gyroControls: false,
          minHeight: 200.0,
          minWidth: 200.0,
          scale: 1.0,
          scaleMobile: 1.0,
          color: 0x55ff99,
          backgroundColor: 0x0a0a0a,
          points: 4,
          maxDistance: 30,
          spacing: 25,
          showDots: false,
        });
        setVantaEffect(effect);
        requestAnimationFrame(() => setReady(true));
      }
    }, { timeout: 200 });

    return () => {
      if (typeof cancelIdleCallback !== "undefined") cancelIdleCallback(handle as number);
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);

  return (
    <div
      ref={vantaRef}
      className="fixed inset-0 z-0"
      style={{
        opacity: ready ? 0.3 : 0,
        transition: "opacity 0.8s ease-in",
      }}
    />
  );
}
