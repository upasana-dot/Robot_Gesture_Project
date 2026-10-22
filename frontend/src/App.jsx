import "./App.css";
import { useEffect, useState } from "react";
import {
  Activity,
  Bot,
  CheckCircle2,
  CircleAlert,
  Clock3,
  Cpu,
  History,
  LoaderCircle,
  Play,
  RotateCcw,
  Send,
  ShieldCheck,
  Workflow,
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8001";

const STEPS = [
  { action: "approach", label: "Approach", description: "Move toward the object" },
  { action: "grasp", label: "Grasp", description: "Grip the selected object" },
  { action: "lift", label: "Lift", description: "Lift the object safely" },
  { action: "move_to", label: "Move to target", description: "Transport to destination" },
  { action: "release", label: "Release", description: "Release at the target" },
];

function StatusBadge({ status }) {
  const value = (status || "unknown").toLowerCase();
  return <span className={`status-badge status-${value}`}>{value}</span>;
}

function App() {
  const [instruction, setInstruction] = useState(
    "Pick up the red cube and move it to the blue zone"
  );
  const [task, setTask] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiOnline, setApiOnline] = useState(false);

  async function checkAPI() {
    try {
      const response = await fetch(`${API}/health`);
      setApiOnline(response.ok);
    } catch {
      setApiOnline(false);
    }
  }

  async function loadHistory() {
    try {
      const response = await fetch(`${API}/api/tasks/`);
      if (!response.ok) throw new Error("Could not load task history");
      const data = await response.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    checkAPI();
    loadHistory();
  }, []);

  async function executeTask(event) {
    event.preventDefault();
    if (!instruction.trim() || loading) return;

    setLoading(true);
    setError("");
    setTask(null);

    try {
      const response = await fetch(`${API}/api/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instruction: instruction.trim() }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail || "Task execution failed")
        );
      }

      setTask(data);
      await loadHistory();
    } catch (err) {
      setError(
        `${err.message}. Check that the RAST backend is running on port 8001.`
      );
    } finally {
      setLoading(false);
      checkAPI();
    }
  }

  async function openTask(taskId) {
    setError("");
    try {
      const response = await fetch(`${API}/api/tasks/${taskId}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to open task");

      setTask({
        ...data,
        task_id: data.id,
        execution_results: [],
      });
      setInstruction(data.instruction || "");
    } catch (err) {
      setError(err.message);
    }
  }

  const actions = task?.actions || [];
  const completed = actions.filter((item) => item.status === "completed").length;
  const taskStatus = task?.status || "idle";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Bot size={25} /></div>
          <div>
            <h1>RAST<span>.</span></h1>
            <p>ROBOTIC INTELLIGENCE</p>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <a className="nav-item active" href="#dashboard">
          <Workflow size={18} /> Dashboard
        </a>
        <a className="nav-item" href="#execution">
          <Activity size={18} /> Execution monitor
        </a>
        <a className="nav-item" href="#history">
          <History size={18} /> Task history
        </a>

        <div className="sidebar-bottom">
          <div className="system-card">
            <div className="system-title">
              <span className={`online-dot ${apiOnline ? "" : "offline"}`} />
              Backend API
              <span className="system-state">{apiOnline ? "ONLINE" : "OFFLINE"}</span>
            </div>
            <p>{API}</p>
            <button className="refresh-button" onClick={checkAPI}>
              <RotateCcw size={14} /> Check connection
            </button>
          </div>
          <p className="sidebar-footer">RAST · DEVELOPMENT BUILD 0.1.0</p>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div>
            <div className="breadcrumb">Workspace <span>/</span> Dashboard</div>
            <h2>Robotics Control Center</h2>
          </div>
          <div className="topbar-right">
            <span className="environment"><span className="online-dot" /> SIMULATION MODE</span>
            <div className="avatar"><Bot size={19} /></div>
          </div>
        </header>

        <section className="welcome">
          <div>
            <div className="eyebrow"><Cpu size={15} /> AI-POWERED ROBOTICS</div>
            <h2>Turn language into <span>action.</span></h2>
            <p>Describe a task in plain English. RAST plans, validates, and executes it in simulation.</p>
          </div>
          <div className="welcome-art"><Bot size={76} strokeWidth={1.1} /><div className="art-ring" /></div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-top"><span>Total tasks</span><History size={18} /></div>
            <strong>{history.length}</strong>
            <small>Saved in task history</small>
          </div>
          <div className="stat-card">
            <div className="stat-top"><span>Completed tasks</span><CheckCircle2 size={18} /></div>
            <strong>{history.filter((item) => item.status === "completed").length}</strong>
            <small>Successfully reported</small>
          </div>
          <div className="stat-card">
            <div className="stat-top"><span>Action sequence</span><Workflow size={18} /></div>
            <strong>05 <span className="stat-unit">steps</span></strong>
            <small>Validated action pipeline</small>
          </div>
          <div className="stat-card">
            <div className="stat-top"><span>AI service</span><Cpu size={18} /></div>
            <strong className="service-value">{apiOnline ? "Ready" : "Offline"}</strong>
            <small>Backend connectivity</small>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel command-panel">
            <div className="panel-heading">
              <div className="heading-icon"><Send size={18} /></div>
              <div><h3>Command interface</h3><p>Give your robot a task</p></div>
            </div>

            <form onSubmit={executeTask}>
              <label htmlFor="instruction">NATURAL LANGUAGE INSTRUCTION</label>
              <textarea
                id="instruction"
                value={instruction}
                onChange={(event) => setInstruction(event.target.value)}
                placeholder="e.g. Pick up the red cube and move it to the blue zone"
                minLength={5}
                maxLength={1000}
                required
                rows={4}
                disabled={loading}
              />
              <div className="input-footer">
                <span>{instruction.length}/1000 characters</span>
                <span><ShieldCheck size={14} /> Validated action planning</span>
              </div>
              <div className="example-row">
                <span>TRY AN EXAMPLE</span>
                <button type="button" onClick={() => setInstruction("Pick up the red cube and move it to the blue zone")} disabled={loading}>Red cube → Blue zone</button>
                <button type="button" onClick={() => setInstruction("Pick up the green cube and move it to the red zone")} disabled={loading}>Green cube → Red zone</button>
              </div>
              <button className="execute-button" type="submit" disabled={loading || !instruction.trim()}>
                {loading ? <LoaderCircle className="spin" size={19} /> : <Play size={18} fill="currentColor" />}
                {loading ? "Executing task..." : "Execute robot task"}
              </button>
              <p className="execution-note"><CircleAlert size={14} /> Runs a PyBullet simulation through your backend.</p>
            </form>
            {error && <div className="error-box"><CircleAlert size={17} /> <span>{error}</span></div>}
          </div>

          <div className="panel pipeline-panel">
            <div className="panel-heading">
              <div className="heading-icon purple"><Workflow size={18} /></div>
              <div><h3>Action pipeline</h3><p>Execution sequence</p></div>
            </div>
            <div className="pipeline">
              {STEPS.map((step, index) => {
                const result = actions.find((item) => item.action === step.action);
                const isDone = result?.status === "completed";
                const isFailed = result?.status === "failed";
                const active = loading && !isDone && !isFailed;
                return (
                  <div className="pipeline-step" key={step.action}>
                    <div className={`step-marker ${isDone ? "done" : ""} ${isFailed ? "failed" : ""} ${active ? "active-step" : ""}`}>
                      {isDone ? <CheckCircle2 size={18} /> : isFailed ? <CircleAlert size={18} /> : <span>{String(index + 1).padStart(2, "0")}</span>}
                    </div>
                    {index < STEPS.length - 1 && <div className={`step-line ${isDone ? "line-done" : ""}`} />}
                    <div className="step-copy">
                      <strong>{step.label}</strong>
                      <p>{step.description}</p>
                    </div>
                    <span className={`step-state ${isDone ? "text-done" : isFailed ? "text-failed" : ""}`}>
                      {isDone ? "DONE" : isFailed ? "FAILED" : result?.status?.toUpperCase() || "WAITING"}
                    </span>
                  </div>
                );
              })}
            </div>
            <div className="pipeline-footer">
              <span>Task status</span>
              <StatusBadge status={taskStatus} />
            </div>
            {task && <p className="task-reference">Task reference: <strong>#{task.task_id ?? task.id}</strong></p>}
          </div>
        </section>

        <section className="panel results-panel" id="execution">
          <div className="panel-heading results-heading">
            <div className="heading-icon green"><Activity size={18} /></div>
            <div><h3>Execution results</h3><p>Recorded output from the API</p></div>
            {task && <StatusBadge status={task.status} />}
          </div>

          {!task ? (
            <div className="empty-state">
              <div className="empty-icon"><Workflow size={27} /></div>
              <strong>No execution selected</strong>
              <p>Submit a command to see the robot's action results here.</p>
            </div>
          ) : (
            <>
              <div className="progress-summary">
                <div><strong>{completed}/{actions.length || 0}</strong><span> actions completed</span></div>
                <div className="progress-track"><div style={{ width: `${actions.length ? (completed / actions.length) * 100 : 0}%` }} /></div>
              </div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>STEP</th><th>ACTION</th><th>OBJECT</th><th>TARGET</th><th>STATUS</th></tr></thead>
                  <tbody>
                    {actions.map((action) => (
                      <tr key={action.id ?? action.step_number}>
                        <td>{String(action.step_number).padStart(2, "0")}</td>
                        <td className="action-name">{action.action}</td>
                        <td>{action.object_name || "—"}</td>
                        <td>{action.target || "—"}</td>
                        <td><StatusBadge status={action.status || "unknown"} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {task.execution_results?.length > 0 && (
                <details className="raw-results">
                  <summary>View simulation details</summary>
                  <pre>{JSON.stringify(task.execution_results, null, 2)}</pre>
                </details>
              )}
            </>
          )}
        </section>

        <section className="panel history-panel" id="history">
          <div className="panel-heading results-heading">
            <div className="heading-icon"><Clock3 size={18} /></div>
            <div><h3>Recent tasks</h3><p>Tasks saved in the RAST database</p></div>
            <button className="refresh-button history-refresh" onClick={loadHistory}><RotateCcw size={14} /> Refresh</button>
          </div>
          {history.length === 0 ? (
            <div className="history-empty">No saved tasks found. Execute your first command above.</div>
          ) : (
            <div className="history-list">
              {history.slice(0, 6).map((item) => (
                <button className="history-row" key={item.id} onClick={() => openTask(item.id)}>
                  <div className="history-task-icon"><Bot size={19} /></div>
                  <div className="history-task-copy">
                    <strong>{item.instruction}</strong>
                    <span>Task #{item.id}{item.created_at ? ` · ${new Date(item.created_at).toLocaleString()}` : ""}</span>
                  </div>
                  <StatusBadge status={item.status} />
                </button>
              ))}
            </div>
          )}
        </section>

        <footer className="page-footer">
          <span>RAST · Robotic Action Sequence Transformer</span>
          <span><span className="online-dot" /> AI planning · Validation · Simulation</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
