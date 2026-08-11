const BACKEND_URL = (process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const CRM_BACKEND_URL = (process.env.CRM_BACKEND_URL ?? "http://127.0.0.1:8001").replace(/\/$/, "");
const COMMUNICATION_BACKEND_URL = (process.env.COMMUNICATION_BACKEND_URL ?? "http://127.0.0.1:8002").replace(/\/$/, "");
const AUTH_BACKEND_URL = (process.env.AUTH_BACKEND_URL ?? "http://127.0.0.1:5000").replace(/\/$/, "");

function resolveTarget(path: string[]) {
  const [service, ...rest] = path;
  if (service === "crm") return { baseUrl: CRM_BACKEND_URL, path: rest };
  if (service === "communications") return { baseUrl: COMMUNICATION_BACKEND_URL, path: rest };
  if (service === "auth-service") return { baseUrl: AUTH_BACKEND_URL, path: ["api", "auth", ...rest] };
  return { baseUrl: BACKEND_URL, path };
}

async function proxy(request: Request, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const incoming = new URL(request.url);
  const destination = resolveTarget(path);
  const target = `${destination.baseUrl}/${destination.path.map(encodeURIComponent).join("/")}${incoming.search}`;
  const headers = new Headers();
  for (const header of ["accept", "authorization", "content-type"]) {
    const value = request.headers.get(header);
    if (value) headers.set(header, value);
  }

  try {
    const response = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.arrayBuffer(),
      cache: "no-store",
    });
    const outgoingHeaders = new Headers();
    for (const header of ["content-type", "content-disposition"]) {
      const value = response.headers.get(header);
      if (value) outgoingHeaders.set(header, value);
    }
    return new Response(response.body, { status: response.status, headers: outgoingHeaders });
  } catch {
    return Response.json(
      { detail: `Backend service is unavailable at ${destination.baseUrl}.` },
      { status: 503 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
