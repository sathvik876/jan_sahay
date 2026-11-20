// src/components/SchemeCard.jsx
import React from "react";

export default function SchemeCard({ scheme, onDetails }) {
  return (
    <article className="scheme-card">
      <div className="scheme-card-top">
        <div className="scheme-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M3 21H21M5 21V10H19V21M8 10V7L12 4L16 7V10M9 14H11M13 14H15M9 17H11M13 17H15" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        {scheme.status && <span className="verified-badge"><span></span>{scheme.status}</span>}
      </div>
      <h3>{scheme.name}</h3>
      <div className="scheme-details">
        {scheme.category && <div><span>Category</span><strong>{scheme.category}</strong></div>}
        {scheme.state && <div><span>Coverage</span><strong>{scheme.state}</strong></div>}
        {scheme.department && <div className="scheme-department"><span>Department</span><strong>{scheme.department}</strong></div>}
      </div>
      <button type="button" className="scheme-button" onClick={() => onDetails?.(scheme)}>
        View details
        <svg viewBox="0 0 20 20" fill="none"><path d="M4 10H16M11 5L16 10L11 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
      </button>
    </article>
  );
}
