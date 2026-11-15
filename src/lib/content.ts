import { getCollection, type CollectionEntry } from "astro:content";
import { marked } from "marked";

export type Pagina = CollectionEntry<"pages">;
export type Blok = Pagina["data"]["blocks"][number];

/** Alle pagina's die niet als concept staan, op volgorde. */
export async function paginas(): Promise<Pagina[]> {
  const alle = await getCollection("pages", (p) => !p.data.draft);
  return alle.sort((a, b) => (a.data.order ?? 99) - (b.data.order ?? 99));
}

/** Het adres van een pagina: home staat op /. */
export const url = (p: Pagina) => (p.id === "home" ? "/" : `/${p.id}`);

/** Pagina's in het menu (zonder home, zonder verborgen pagina's). */
export async function menu() {
  return (await paginas()).filter((p) => p.id !== "home" && p.data.listed).map((p) => ({ titel: p.data.title, url: url(p) }));
}

/** Markdown uit een CMS-veld naar HTML. `inline` voor korte teksten zonder <p>. */
export function md(tekst: string | undefined, inline = false): string {
  if (!tekst) return "";
  return inline ? (marked.parseInline(tekst) as string) : (marked.parse(tekst, { breaks: false }) as string);
}
