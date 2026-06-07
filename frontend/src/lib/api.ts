const BASE = '';

export async function apiGet(path: string): Promise<any> {
  try {
    const res = await fetch(`${BASE}${path}`);
    return await res.json();
  } catch {
    return null;
  }
}

export async function apiPost(path: string, body: any): Promise<any> {
  try {
    const res = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return await res.json();
  } catch {
    return null;
  }
}
