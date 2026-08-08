const BACKEND_URL = (process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

async function proxy(request: Request, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const incoming = new URL(request.url);
  const target = `${BACKEND_URL}/${path.join("/")}${incoming.search}`;
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

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
      { detail: `Backend is unavailable at ${BACKEND_URL}. Start FastAPI with uvicorn main:app --reload.` },
      { status: 503 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
