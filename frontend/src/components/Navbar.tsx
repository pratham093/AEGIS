"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "./ThemeProvider";
import { useEffect, useRef } from "react";

interface NavbarProps {
  extra?: React.ReactNode;
}

export default function Navbar({ extra }: NavbarProps) {
  const pathname = usePathname();
  const { theme, toggle } = useTheme();
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const nav = navRef.current;
    if (!nav) return;

    const onMouse = (e: MouseEvent) => {
      const links = nav.querySelectorAll("[data-nav-link]");
      links.forEach((el) => {
        const rect = el.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dist = Math.sqrt((e.clientX - cx) ** 2 + (e.clientY - cy) ** 2);
        const proximity = Math.max(0, 1 - dist / 200);
        const htmlEl = el as HTMLElement;

        if (proximity > 0.05) {
          htmlEl.style.textShadow = `0 0 ${proximity * 20}px rgba(34,197,94,${proximity * 0.6})`;
          htmlEl.style.color = `rgba(34,197,94,${0.5 + proximity * 0.5})`;
        } else {
          htmlEl.style.textShadow = "none";
          const isActive = htmlEl.dataset.active === "true";
          htmlEl.style.color = isActive ? "var(--foreground)" : "var(--muted)";
        }
      });
    };

    window.addEventListener("mousemove", onMouse);
    return () => window.removeEventListener("mousemove", onMouse);
  }, []);

  const links = [
    { href: "/", label: "Home" },
    { href: "/learn", label: "Learn" },
    { href: "/signals", label: "Signals" },
  ];

  return (
    <nav ref={navRef} className="flex items-center justify-between px-8 py-4 border-b" style={{ borderColor: "var(--card-border)" }}>
      <Link href="/" className="flex items-center gap-3">
        <img src="/dark.png" alt="AEGIS" className="h-12 dark-logo" />
        <img src="/light.png" alt="AEGIS" className="h-12 light-logo" />
        <span className="text-xl font-bold tracking-tight">AEGIS</span>
      </Link>

      <div className="flex items-center gap-5 text-sm">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            data-nav-link
            data-active={pathname === link.href ? "true" : "false"}
            className={`transition-all duration-150 ${pathname === link.href ? "font-semibold" : ""}`}
            style={{ color: pathname === link.href ? "var(--foreground)" : "var(--muted)" }}
          >
            {link.label}
          </Link>
        ))}

        {extra}

        <button
          onClick={toggle}
          className="p-2 rounded-lg border transition-colors hover:border-[#22c55e]"
          style={{ borderColor: "var(--card-border)" }}
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="5" />
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>

        <Link href="/signals" className="font-semibold px-5 py-2 rounded-lg bg-[#22c55e] text-black hover:bg-[#16a34a] transition-colors">
          Launch App
        </Link>
      </div>
    </nav>
  );
}
