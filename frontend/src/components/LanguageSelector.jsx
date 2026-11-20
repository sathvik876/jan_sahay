// src/components/LanguageSelector.jsx
import React from "react";

const options = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी" },
  { code: "te", label: "తెలుగు" },
];

export default function LanguageSelector({ language, setLanguage }) {
  return (
    <div className="language-selector">
      <span>Language</span>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="rounded border p-1"
      >
        {options.map((opt) => (
          <option key={opt.code} value={opt.code}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
