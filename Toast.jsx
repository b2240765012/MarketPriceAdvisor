import React, { useEffect } from "react";
import "../styles/toast.css";

const TONE_CLASS = {
  info: "toast-info",
  guard: "toast-guard",
  amber: "toast-amber",
  error: "toast-error",
};

export default function Toast({ toast, onDone }) {
  useEffect(() => {
    const t = setTimeout(onDone, 4500);
    return () => clearTimeout(t);
  }, [toast, onDone]);

  return (
    <div className={`toast ${TONE_CLASS[toast.tone] || "toast-info"}`} role="status">
      {toast.message}
    </div>
  );
}
