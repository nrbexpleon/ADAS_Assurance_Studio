const q = id => document.getElementById(id);

q("run").onclick = async () => {
  q("status").textContent = "Running…";
  try {
    const response = await fetch("/api/runs", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({demo: {frames: 100, seed: 42}})
    });
    const report = await response.json();
    if (!response.ok) throw new Error(report.error || `HTTP ${response.status}`);
    q("decision").textContent = report.decision;
    q("precision").textContent = `${(report.perception.precision * 100).toFixed(1)}%`;
    q("recall").textContent = `${(report.perception.recall * 100).toFixed(1)}%`;
    q("odd").textContent = `${report.odd.filter(item => item.state === "inside").length}/${report.odd.length}`;
    q("gates").replaceChildren(...Object.entries(report.gates).map(([name, passed]) => {
      const line = document.createElement("p");
      line.className = passed ? "pass" : "fail";
      const label = document.createElement("b");
      label.textContent = name;
      line.append(label, ` ${passed ? "PASS" : "REVIEW"}`);
      return line;
    }));
    q("status").textContent = `Run ${report.run_id} complete`;
  } catch (error) {
    q("status").textContent = error.message;
  }
};
