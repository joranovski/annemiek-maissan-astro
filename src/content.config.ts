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
    // Velden die elk blok kan hebben: een klein woord boven de kop en de kleur van de sectie
    const label = z.string().optional();
    const toon = z.enum(["auto", "licht", "donker"]).default("auto");
    const knoppen = z.array(z.object({ label: z.string(), link: z.string() })).default([]);
    const hero = z.object({
      type: z.literal("hero"),
      label,
      titel: tekst,
      tekst,
      foto: image().optional(),
      fotoAlt: tekst,
      fotoFocus: z.enum(["boven", "midden", "onder"]).default("midden"),
      uitlijning: z.enum(["links", "midden", "rechts"]).default("links"),
      knoppen,
    });
    const punten = z.object({
      type: z.literal("punten"),
      label,
      toon,
      kop: tekst,
      intro: tekst,
      punten: z.array(z.string()).default([]),
      afsluiting: tekst,
    });
    const tekstblok = z.object({
      type: z.literal("tekst"),
      label,
      toon,
      kop: tekst,
      tekst,
      foto: image().optional(),
      fotoAlt: tekst,
      knoppen,
    });
    const fotos = z.object({
      type: z.literal("fotos"),
      label,
      toon,
      kop: tekst,
      fotos: z.array(z.object({ src: image(), alt: tekst, bijschrift: tekst })).default([]),
    });
    const prijzen = z.object({
      type: z.literal("prijzen"),
      label,
      toon,
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
    const formulier = z.object({ type: z.literal("formulier"), label, toon, kop: tekst, intro: tekst });

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
