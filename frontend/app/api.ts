const BASE_URL = "http://127.0.0.1:8000";

export async function uploadCsv(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

export async function getPreview(datasetId: string, n = 5) {
  const res = await fetch(`${BASE_URL}/datasets/${datasetId}/preview?n=${n}`);

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Preview failed");
  }

  return res.json();
}

export async function getProfile(datasetId: string) {
  const res = await fetch(`${BASE_URL}/datasets/${datasetId}/profile`);

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Profile failed");
  }

  return res.json();
}

export async function explainProfile(datasetId: string) {
  const res = await fetch(`http://127.0.0.1:8000/datasets/${datasetId}/explain`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Explain failed");
  }

  return res.json();
}

export async function getColumns(datasetId: string) {
  const res = await fetch(`http://127.0.0.1:8000/datasets/${datasetId}/columns`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Get columns failed");
  }
  return res.json();
}

export async function explainColumn(datasetId: string, column: string) {
  const url = new URL(`http://127.0.0.1:8000/datasets/${datasetId}/explain-column`);
  url.searchParams.set("column", column);

  const res = await fetch(url.toString(), { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Explain column failed");
  }
  return res.json();
}

export async function getFeatureIdeas(datasetId: string) {
  const res = await fetch(`http://127.0.0.1:8000/datasets/${datasetId}/feature-ideas`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Feature ideas failed");
  }

  return res.json();
}
