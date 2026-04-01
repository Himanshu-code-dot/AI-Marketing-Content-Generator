import { useState } from "react";

function App() {
  const [idea, setIdea] = useState("");
  const [slogan, setSlogan] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const generateSlogan = async () => {
    if (!idea.trim()) return;

    setLoading(true);
    setError("");
    setSlogan("");
    setCopied(false);

    try {
      const response = await fetch("http://127.0.0.1:8000/generate-slogan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: idea }),
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();

      // IMPORTANT: your backend returns "output"
      setSlogan(data.output);
    } catch (err) {
      setError("Error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !loading) {
      generateSlogan();
    }
  };

  const handleCopy = () => {
    if (!slogan) return;
    navigator.clipboard.writeText(slogan);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a0a0a",
        color: "white",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "20px",
        fontFamily: "sans-serif",
      }}
    >
      <div style={{ width: "100%", maxWidth: "500px" }}>
        <h1 style={{ textAlign: "center" }}>
          AI <span style={{ color: "#f59e0b" }}>Slogan Generator</span>
        </h1>

        <p style={{ textAlign: "center", color: "#aaa" }}>
          Enter your idea and generate slogans
        </p>

        <textarea
          rows={3}
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g. fitness app for beginners"
          style={{
            width: "100%",
            padding: "10px",
            marginTop: "15px",
            borderRadius: "8px",
            border: "1px solid #333",
            background: "#111",
            color: "white",
          }}
        />

        <button
          onClick={generateSlogan}
          disabled={loading || !idea.trim()}
          style={{
            width: "100%",
            marginTop: "10px",
            padding: "10px",
            background: "#f59e0b",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          {loading ? "Generating..." : "Generate Slogan"}
        </button>

        {error && (
          <p style={{ color: "red", marginTop: "10px" }}>{error}</p>
        )}

        {slogan && (
          <div
            style={{
              marginTop: "20px",
              padding: "15px",
              border: "1px solid #444",
              borderRadius: "10px",
            }}
          >
            <h3>Generated Slogan:</h3>
            <p>{slogan}</p>

            <button
              onClick={handleCopy}
              style={{
                marginTop: "10px",
                padding: "5px 10px",
                cursor: "pointer",
              }}
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;