// src/App.jsx
import React, { useState } from "react";
import LanguageSelector from "./components/LanguageSelector";
import ChatBox from "./components/ChatBox";
import SchemeCard from "./components/SchemeCard";
import FeatureGrid from "./components/FeatureGrid";
import EligibilityModal from "./components/EligibilityModal";

export default function App() {
  const [language, setLanguage] = useState("en");
  const [schemes, setSchemes] = useState([]);
  const [activeModal, setActiveModal] = useState(null);
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [exploreQuery, setExploreQuery] = useState("");

  const handleNewSchemes = (newSchemes) => {
    setSchemes(newSchemes);
  };

  const handleFeature = (feature) => {
    if (feature === "eligibility") setActiveModal("eligibility");
    if (feature === "document") document.querySelector(".upload-button input")?.click();
    if (feature === "explore") setActiveModal("explore");
    if (feature === "chat") document.querySelector(".chat-compose textarea")?.focus();
  };

  const visibleSchemes = schemes.filter((scheme) => {
    const haystack = `${scheme.name} ${scheme.category} ${scheme.department} ${scheme.state}`.toLowerCase();
    return haystack.includes(exploreQuery.toLowerCase());
  });

  return (
    <main className="app-shell">
      <div className="page-container">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 3L4.5 6.3V11.4C4.5 16.1 7.7 20.3 12 21.5C16.3 20.3 19.5 16.1 19.5 11.4V6.3L12 3Z" stroke="currentColor" strokeWidth="1.7"/>
                <path d="M8.5 12L10.8 14.3L15.8 9.2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <h1>JanSahay AI</h1>
              <p>Citizen Assistance</p>
            </div>
          </div>
          <LanguageSelector language={language} setLanguage={setLanguage} />
        </header>

        <section className="hero">
          <div>
            <span className="hero-eyebrow">YOUR DIGITAL CITIZEN ASSISTANT</span>
            <h2>Find the right government support</h2>
            <p>Ask in your preferred language and discover schemes, eligibility requirements, and next steps.</p>
          </div>
          <div className="hero-status"><span></span> Assistant available</div>
        </section>

        <FeatureGrid onSelect={handleFeature} />

        <section className="chat-card">
          <ChatBox language={language} onSchemes={handleNewSchemes} />
        </section>
        {schemes.length > 0 && (
          <section className="schemes-section">
            <div className="section-heading">
              <div>
                <span>DISCOVER</span>
                <h2>Relevant schemes</h2>
              </div>
              <p>{schemes.length} {schemes.length === 1 ? "scheme" : "schemes"} found</p>
            </div>
            <div className="scheme-grid">
              {schemes.map((scheme) => (
                <SchemeCard key={scheme.id} scheme={scheme} onDetails={setSelectedScheme} />
              ))}
            </div>
          </section>
        )}
      </div>

      {activeModal === "eligibility" && (
        <EligibilityModal schemes={schemes} onClose={() => setActiveModal(null)} />
      )}
      {activeModal === "explore" && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && setActiveModal(null)}>
          <section className="modal-panel explore-modal" role="dialog" aria-modal="true">
            <div className="modal-header">
              <div><span>SCHEME DIRECTORY</span><h2>Explore schemes</h2></div>
              <button type="button" onClick={() => setActiveModal(null)} aria-label="Close">×</button>
            </div>
            <input className="directory-search" value={exploreQuery} onChange={(e) => setExploreQuery(e.target.value)} placeholder="Search students, farmers, pensions..." />
            <div className="directory-grid">
              {visibleSchemes.map((scheme) => (
                <SchemeCard key={scheme.id} scheme={scheme} onDetails={(item) => { setActiveModal(null); setSelectedScheme(item); }} />
              ))}
              {visibleSchemes.length === 0 && <p className="empty-directory">No matching schemes found.</p>}
            </div>
          </section>
        </div>
      )}
      {selectedScheme && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && setSelectedScheme(null)}>
          <section className="modal-panel details-modal" role="dialog" aria-modal="true">
            <div className="modal-header">
              <div><span>SCHEME DETAILS</span><h2>{selectedScheme.name}</h2></div>
              <button type="button" onClick={() => setSelectedScheme(null)} aria-label="Close">×</button>
            </div>
            <div className="details-grid">
              <div><span>Category</span><strong>{selectedScheme.category || "General"}</strong></div>
              <div><span>Coverage</span><strong>{selectedScheme.state || "All India"}</strong></div>
            </div>
            <h3>Application checklist</h3>
            <ul>
              <li>Identity proof and recent photograph</li>
              <li>Income certificate, if applicable</li>
              <li>Residence and category certificates</li>
              <li>Bank account details for direct benefit transfer</li>
            </ul>
            <p className="source-note">Requirements may vary. Verify the official notification before applying.</p>
            <a className="primary-modal-button" href="https://services.india.gov.in/" target="_blank" rel="noreferrer">Visit official India portal</a>
          </section>
        </div>
      )}
    </main>
  );
}
