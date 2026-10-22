const API_URL = "http://localhost:8000";

export async function createTask(instruction) {
  const response = await fetch(`${API_URL}/api/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ instruction }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Unable to generate plan");
  }

  return data;
}

export async function getTasks() {
  const response = await fetch(`${API_URL}/api/tasks`);

  if (!response.ok) {
    throw new Error("Unable to load task history");
  }

  return response.json();
}