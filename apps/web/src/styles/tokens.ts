/**
 * Design Tokens for Sketch2STEP Enterprise.
 * Precision engineering aesthetic: Cool neutrals, coolant-teal accent,
 * amber strictly for human attention, red for errors, green for verified.
 * Typography: IBM Plex Sans for UI, IBM Plex Mono for numbers.
 */

export const tokens = {
  colors: {
    bg: {
      canvas: "#090d12",
      panel: "#111720",
      card: "#141d28",
      cardHover: "#1c2635",
      input: "#0b1017",
    },
    border: {
      subtle: "#1c2734",
      default: "#222f3e",
      focus: "#06b6d4",
    },
    accent: {
      teal: "#06b6d4",
      tealHover: "#22d3ee",
      tealMuted: "rgba(6, 182, 212, 0.15)",
    },
    status: {
      verified: {
        text: "#34d399",
        bg: "rgba(16, 185, 129, 0.15)",
        border: "rgba(16, 185, 129, 0.4)",
        dot: "#10b981",
      },
      needsHuman: {
        text: "#fbbf24",
        bg: "rgba(245, 158, 11, 0.15)",
        border: "rgba(245, 158, 11, 0.4)",
        dot: "#f59e0b",
      },
      confirmed: {
        text: "#38bdf8",
        bg: "rgba(56, 189, 248, 0.15)",
        border: "rgba(56, 189, 248, 0.4)",
        dot: "#38bdf8",
      },
      error: {
        text: "#f87171",
        bg: "rgba(239, 68, 68, 0.15)",
        border: "rgba(239, 68, 68, 0.4)",
        dot: "#ef4444",
      },
    },
    text: {
      primary: "#f1f5f9",
      secondary: "#94a3b8",
      muted: "#64748b",
      code: "#e2e8f0",
    },
  },
  typography: {
    fontSans: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif",
    fontMono: "'IBM Plex Mono', monospace",
  },
} as const;
