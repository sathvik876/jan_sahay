import React, { useState } from "react";

export default function EligibilityModal({ schemes, onClose }) {
  const [form, setForm] = useState({ age: "", state: "", income: "", occupation: "" });
  const [results, setResults] = useState(null);

  const check = async (event) => {
    event.preventDefault();
    const data = await Promise.all(schemes.map(async (scheme) => {
      try {
        const response = await fetch("/api/eligibility/check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ scheme_id: scheme.id, user_data: form }),
        });
        if (!response.ok) return { ...scheme, status: "needs_more_info" };
        return { ...scheme, ...(await response.json()) };
      } catch {
        return { ...scheme, status: "needs_more_info" };
      }
    }));
    setResults(data);
  };

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="modal-panel eligibility-modal" role="dialog" aria-modal="true" aria-labelledby="eligibility-title">
        <div className="modal-header">
          <div><span>PERSONALISED MATCH</span><h2 id="eligibility-title">Check eligibility</h2></div>
          <button type="button" onClick={onClose} aria-label="Close">×</button>
        </div>
        {!results ? (
          <form className="eligibility-form" onSubmit={check}>
            <label>Age<input type="number" min="0" max="120" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} placeholder="For example, 22" /></label>
            <label>State<select value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })}><option value="">Select state</option><option>Telangana</option><option>Andhra Pradesh</option><option>Other</option></select></label>
            <label>Occupation<select value={form.occupation} onChange={(e) => setForm({ ...form, occupation: e.target.value })}><option value="">Select occupation</option><option>Student</option><option>Farmer</option><option>Employed</option><option>Senior citizen</option><option>Other</option></select></label>
            <label>Annual family income (₹)<input type="number" min="0" value={form.income} onChange={(e) => setForm({ ...form, income: e.target.value })} placeholder="For example, 150000" /></label>
            <button type="submit" className="primary-modal-button">Find matching schemes</button>
          </form>
        ) : (
          <div className="eligibility-results">
            {results.map((result) => (
              <article key={result.id}>
                <div><strong>{result.name}</strong><span>{result.status.replaceAll("_", " ")}</span></div>
                {result.missing_fields?.length > 0 && <p>Needs verification: {result.missing_fields.join(", ")}</p>}
                {result.status === "eligible" && <p>You appear to meet the available local criteria.</p>}
              </article>
            ))}
            <button type="button" className="secondary-modal-button" onClick={() => setResults(null)}>Edit details</button>
          </div>
        )}
      </section>
    </div>
  );
}
