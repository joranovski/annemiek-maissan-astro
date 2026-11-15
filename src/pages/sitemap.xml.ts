import type { APIRoute } from "astro";
import { paginas, url } from "../lib/content";

// Alle pagina's behalve verborgen en concepten; /admin, /bedankt en 404 niet.
export const GET: APIRoute = async ({ site }) => {
  const regels = (await paginas()).map((p) => `  <url><loc>${new URL(url(p), site).href}</loc></url>`);
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${regels.join("\n")}\n</urlset>\n`;
  return new Response(xml, { headers: { "Content-Type": "application/xml" } });
};
