import React from "react";

const features = [
  { id: "chat", title: "AI Assistant", text: "Ask questions", icon: "chat" },
  { id: "eligibility", title: "Check Eligibility", text: "Find matching schemes", icon: "check" },
  { id: "document", title: "Analyze Documents", text: "Understand notices", icon: "document" },
  { id: "explore", title: "Explore Schemes", text: "Browse benefits", icon: "search" },
];

function Icon({ name }) {
  if (name === "chat") return <svg viewBox="0 0 24 24" fill="none"><path d="M6 18.5V21L9.5 18.5H17C18.7 18.5 20 17.2 20 15.5V7C20 5.3 18.7 4 17 4H7C5.3 4 4 5.3 4 7V15.5C4 17.2 5.3 18.5 7 18.5H6Z" stroke="currentColor" strokeWidth="1.6"/><circle cx="9" cy="11" r="1" fill="currentColor"/><circle cx="12" cy="11" r="1" fill="currentColor"/><circle cx="15" cy="11" r="1" fill="currentColor"/></svg>;
  if (name === "check") return <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6"/><path d="M7.5 12L10.5 15L16.5 9" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"/></svg>;
  if (name === "document") return <svg viewBox="0 0 24 24" fill="none"><path d="M7 3H15L19 7V21H7V3Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/><path d="M15 3V8H19M10 12H16M10 15H16M10 18H14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>;
  return <svg viewBox="0 0 24 24" fill="none"><circle cx="10.5" cy="10.5" r="6.5" stroke="currentColor" strokeWidth="1.6"/><path d="M15.5 15.5L20 20" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>;
}

export default function FeatureGrid({ onSelect }) {
  return (
    <section className="feature-grid" aria-label="Main services">
      {features.map((feature) => (
        <button key={feature.id} type="button" className="feature-card" onClick={() => onSelect(feature.id)}>
          <span className="feature-icon"><Icon name={feature.icon} /></span>
          <span className="feature-copy">
            <strong>{feature.title}</strong>
            <small>{feature.text}</small>
          </span>
          <svg className="feature-arrow" viewBox="0 0 20 20" fill="none"><path d="M4 10H16M11 5L16 10L11 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
        </button>
      ))}
    </section>
  );
}
