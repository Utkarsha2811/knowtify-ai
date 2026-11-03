import React, { useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
const OUTPUTS = [
  { id: "summary", label: "Summary", icon: "✦", description: "Clear revision notes" },
  { id: "flashcards", label: "Flashcards", icon: "▣", description: "Question and answer cards" },
  { id: "quiz", label: "Quiz", icon: "✓", description: "Multiple-choice practice" },
];

function App() {
  const fileInput = useRef(null);
  const [file, setFile] = useState(null);
  const [material, setMaterial] = useState(null);
  const [activeOutput, setActiveOutput] = useState("summary");
  const [focusTopic, setFocusTopic] = useState("overall revision");
  const [count, setCount] = useState(5);
  const [loading, setLoading] = useState("");
  const [result, setResult] = useState(null);
  const [notice, setNotice] = useState({ type: "info", text: "Choose a document to begin." });
  const [dragging, setDragging] = useState(false);

  function selectFile(selectedFile) {
    if (!selectedFile) return;
    const extension = selectedFile.name.split(".").pop()?.toLowerCase();

    if (!["txt", "md", "pdf"].includes(extension)) {
      setNotice({ type: "error", text: "Please choose a PDF, TXT, or Markdown file." });
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setNotice({ type: "error", text: "The file must be smaller than 10 MB." });
      return;
    }

    setFile(selectedFile);
    setMaterial(null);
    setResult(null);
    setNotice({ type: "info", text: `${selectedFile.name} is ready to upload.` });
  }

  async function uploadMaterial() {
    if (!file) return;

    setLoading("upload");
    setNotice({ type: "info", text: "Reading and preparing your document…" });

    try {
      const formData = new FormData();
      formData.append("file", file);
      const data = await apiRequest("/upload", { method: "POST", body: formData });

      setMaterial(data);
      setNotice({
        type: "success",
        text: `Ready — ${data.chunk_count} passages prepared from ${data.filename}.`,
      });
    } catch (error) {
      setNotice({ type: "error", text: error.message });
    } finally {
      setLoading("");
    }
  }

  async function generate() {
    if (!material) {
      setNotice({ type: "error", text: "Upload your document before generating study material." });
      return;
    }

    setLoading(activeOutput);
    setResult(null);
    setNotice({ type: "info", text: `Creating your ${activeOutput} from the uploaded source…` });

    try {
      const payload = { material_id: material.material_id, count };
      if (activeOutput === "summary") payload.focus_topic = focusTopic;

      const data = await apiRequest(`/generate/${activeOutput}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      setResult({ type: activeOutput, data });
      setNotice({
        type: "success",
        text: `${OUTPUTS.find((item) => item.id === activeOutput).label} generated from your source.`,
      });
    } catch (error) {
      setNotice({ type: "error", text: error.message });
    } finally {
      setLoading("");
    }
  }

  function resetFile() {
    setFile(null);
    setMaterial(null);
    setResult(null);
    if (fileInput.current) fileInput.current.value = "";
    setNotice({ type: "info", text: "Choose a document to begin." });
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="#" aria-label="Knowtify AI home">
          <span className="brand-mark">K</span>
          <span>knowtify</span>
        </a>
        <span className="header-badge"><span className="pulse" /> Grounded AI</span>
      </header>

      <main>
        <section className="hero">
          <p className="eyebrow">Your notes, made useful</p>
          <h1>Study less. <em>Understand more.</em></h1>
          <p className="hero-copy">
            Turn your course material into focused notes, flashcards, and practice questions —
            grounded only in what you upload.
          </p>
          <div className="trust-row" aria-label="Product benefits">
            <span>✓ Source-grounded</span>
            <span>✓ No account required</span>
            <span>✓ Human review encouraged</span>
          </div>
        </section>

        <section className="workspace" aria-label="Study material generator">
          <div className="step-card upload-card">
            <div className="step-heading">
              <span className="step-number">01</span>
              <div>
                <h2>Add your material</h2>
                <p>PDF, TXT, or Markdown · up to 10 MB</p>
              </div>
            </div>

            {!file ? (
              <button
                className={`drop-zone ${dragging ? "is-dragging" : ""}`}
                onClick={() => fileInput.current?.click()}
                onDragEnter={(event) => { event.preventDefault(); setDragging(true); }}
                onDragOver={(event) => event.preventDefault()}
                onDragLeave={() => setDragging(false)}
                onDrop={(event) => {
                  event.preventDefault();
                  setDragging(false);
                  selectFile(event.dataTransfer.files[0]);
                }}
                type="button"
              >
                <span className="upload-icon">↑</span>
                <strong>Drop your study material here</strong>
                <span>or click to browse your files</span>
              </button>
            ) : (
              <div className="selected-file">
                <span className="file-icon">{file.name.toLowerCase().endsWith(".pdf") ? "PDF" : "TXT"}</span>
                <div className="file-details">
                  <strong>{file.name}</strong>
                  <span>{formatBytes(file.size)}{material ? ` · ${material.chunk_count} passages` : ""}</span>
                </div>
                <button className="icon-button" onClick={resetFile} aria-label="Remove file">×</button>
              </div>
            )}

            <input
              ref={fileInput}
              className="sr-only"
              type="file"
              accept=".txt,.md,.pdf"
              onChange={(event) => selectFile(event.target.files[0])}
            />
            {file && !material && (
              <button className="primary-button full-width" onClick={uploadMaterial} disabled={Boolean(loading)}>
                {loading === "upload" ? <><span className="spinner" /> Preparing document…</> : "Prepare document →"}
              </button>
            )}
            {material && <div className="prepared-note">✓ Document prepared and ready to study</div>}
          </div>

          <div className={`step-card generate-card ${!material ? "is-locked" : ""}`}>
            <div className="step-heading">
              <span className="step-number">02</span>
              <div>
                <h2>Choose what to create</h2>
                <p>Every answer uses your uploaded source</p>
              </div>
            </div>

            <div className="output-tabs" role="tablist" aria-label="Output type">
              {OUTPUTS.map((output) => (
                <button
                  className={activeOutput === output.id ? "active" : ""}
                  key={output.id}
                  onClick={() => { setActiveOutput(output.id); setResult(null); }}
                  role="tab"
                  aria-selected={activeOutput === output.id}
                >
                  <span className="tab-icon">{output.icon}</span>
                  <span><strong>{output.label}</strong><small>{output.description}</small></span>
                </button>
              ))}
            </div>

            <div className="options-row">
              {activeOutput === "summary" ? (
                <label className="field">
                  <span>Focus topic <small>optional</small></span>
                  <input value={focusTopic} onChange={(event) => setFocusTopic(event.target.value)} />
                </label>
              ) : (
                <label className="field">
                  <span>Number of {activeOutput === "quiz" ? "questions" : "cards"}</span>
                  <select value={count} onChange={(event) => setCount(Number(event.target.value))}>
                    {[3, 5, 8, 10].map((value) => <option key={value} value={value}>{value}</option>)}
                  </select>
                </label>
              )}
              <button className="primary-button generate-button" onClick={generate} disabled={!material || Boolean(loading)}>
                {loading && loading !== "upload"
                  ? <><span className="spinner" /> Generating…</>
                  : `Generate ${OUTPUTS.find((item) => item.id === activeOutput).label} →`}
              </button>
            </div>
          </div>
        </section>

        <div className={`notice ${notice.type}`} role="status">
          <span>{notice.type === "success" ? "✓" : notice.type === "error" ? "!" : "i"}</span>
          {notice.text}
        </div>

        {result && <Results result={result} />}

        <section className="quality-note">
          <div className="quality-icon">◎</div>
          <div>
            <strong>AI supports your learning — it does not replace review.</strong>
            <p>Knowtify limits generation to retrieved source passages. Always verify important facts against the original document.</p>
          </div>
        </section>
      </main>

      <footer>
        <span>Knowtify AI · Built for focused learning</span>
        <span>Flask · React · LangChain</span>
      </footer>
    </div>
  );
}

function Results({ result }) {
  if (result.type === "summary") {
    const points = result.data.summary
      .split("\n")
      .map((line) => line.replace(/^[-•]\s*/, "").trim())
      .filter(Boolean);

    return (
      <section className="results-section">
        <div className="results-heading"><span>✦</span><div><h2>Your revision notes</h2><p>Generated from the most relevant source passages</p></div></div>
        <div className="summary-list">
          {points.map((point, index) => <div className="summary-point" key={`${point}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><p>{point}</p></div>)}
        </div>
      </section>
    );
  }

  if (result.type === "flashcards") {
    return (
      <section className="results-section">
        <div className="results-heading"><span>▣</span><div><h2>Your flashcards</h2><p>Click a card to reveal the answer</p></div></div>
        <div className="flashcard-grid">
          {result.data.flashcards.map((card, index) => <Flashcard key={`${card.question}-${index}`} card={card} number={index + 1} />)}
        </div>
      </section>
    );
  }

  return (
    <section className="results-section">
      <div className="results-heading"><span>✓</span><div><h2>Your practice quiz</h2><p>Answer first, then reveal the source-grounded answer</p></div></div>
      <div className="quiz-list">
        {result.data.quiz.map((question, index) => <QuizQuestion key={`${question.question}-${index}`} item={question} number={index + 1} />)}
      </div>
    </section>
  );
}

function Flashcard({ card, number }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <button className={`flashcard ${revealed ? "revealed" : ""}`} onClick={() => setRevealed(!revealed)}>
      <span className="card-number">Card {number}</span>
      <strong>{revealed ? card.answer : card.question}</strong>
      <small>{revealed ? "Click to see question" : "Click to reveal answer"}</small>
    </button>
  );
}

function QuizQuestion({ item, number }) {
  const [showAnswer, setShowAnswer] = useState(false);
  return (
    <article className="quiz-question">
      <p className="question-label">Question {number}</p>
      <h3>{item.question}</h3>
      <div className="answer-options">
        {item.options.map((option, index) => <div key={`${option}-${index}`}><span>{String.fromCharCode(65 + index)}</span>{option}</div>)}
      </div>
      <button className="text-button" onClick={() => setShowAnswer(!showAnswer)}>
        {showAnswer ? `Answer: ${item.answer}` : "Reveal answer"}
      </button>
    </article>
  );
}

async function apiRequest(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error("Could not reach the backend. Make sure Flask is running on port 5000.");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Something went wrong. Please try again.");
  return data;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
