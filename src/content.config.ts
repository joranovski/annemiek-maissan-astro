import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

// Eén map per pagina: src/content/pages/<slug>/index.md met de foto's ernaast.
// De inhoud staat in `blocks`: een lijst blokken die Annemiek in het CMS kan toevoegen en verschuiven.
const pages = defineCollection({
  loader: glob({
    pattern: "*/index.md",
    base: "./src/content/pages",
    generateId: ({ entry }) => entry.replace(/\/index\.md$/, ""),
  }),
  schema: ({ image }) => {
    const tekst = z.string().optional();
    const hero = z.object({
      type: z.literal("hero"),
      titel: tekst,
      tekst,
      foto: image().optional(),
      fotoAlt: tekst,
      fotoFocus: z.enum(["boven", "midden", "onder"]).default("midden"),
      uitlijning: z.enum(["links", "midden", "rechts"]).default("links"),
    });
    const punten = z.object({
      type: z.literal("punten"),
      kop: tekst,
      intro: tekst,
      punten: z.array(z.string()).default([]),
      afsluiting: tekst,
    });
    const tekstblok = z.object({
      type: z.literal("tekst"),
      kop: tekst,
      tekst,
      foto: image().optional(),
      fotoAlt: tekst,
      knoppen: z.array(z.object({ label: z.string(), link: z.string() })).default([]),
    });
    const fotos = z.object({
      type: z.literal("fotos"),
      kop: tekst,
      fotos: z.array(z.object({ src: image(), alt: tekst, bijschrift: tekst })).default([]),
    });
    const prijzen = z.object({
      type: z.literal("prijzen"),
      kop: tekst,
      subkop: tekst,
      pakketten: z
        .array(
          z.object({
            naam: z.string(),
            omschrijving: tekst,
            prijs: z.string(),
            toelichting: tekst,
            populair: z.boolean().default(false),
          }),
        )
        .default([]),
    });
    const formulier = z.object({ type: z.literal("formulier"), kop: tekst, intro: tekst });

    return z.object({
      title: z.string(),
      order: z.number().optional(),
      listed: z.boolean().default(true),
      draft: z.boolean().default(false),
      metaTitle: tekst,
      metaDescription: tekst,
      blocks: z.array(z.discriminatedUnion("type", [hero, punten, tekstblok, fotos, prijzen, formulier])).default([]),
    });
  },
});

export const collections = { pages };
