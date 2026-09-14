# Sebastian demo — human explanatory video script

**Style:** like you’re screen-sharing with a colleague and walking him through it  
**Not:** ad voiceover / pitch deck narration  
**Length:** ~40–50 seconds spoken (slightly slower than the hard cut MP4 — pause on key frames if needed)  
**Video:** `sebastian_floorplan_demo.mp4` · or live UI recording

---

## Main script (read this)

Hey Sebastian — just wanted to quickly show you what we meant with the floor-plan stuff.

So basically, you start with a normal 2D drawing — the kind of plan you’d already have for a building.  
I’m dropping in a furnished apartment plan here.

Then we run detection on it.  
What you’re seeing now are the objects the model picks up — doors, windows, furniture like the bed, sofa, tables — marked directly on the plan.

If I put original and detected next to each other, it’s easier to see what changed.  
Left is the drawing as-is. Right is after the model has labeled what’s in the space.

It also works on cleaner CAD plans, not only these interior-style ones.  
Same idea — openings, rooms, furniture inventory.

And the useful part for teams like yours is the output isn’t just an image.  
You get a structured list — what’s detected, which rooms, and JSON you can actually use downstream for building or energy workflows.

That’s the whole loop: upload the plan, detect what’s in it, get structured data out.  
If you want, we can try it on one of your real drawings next.

---

## Timed to the current video (with natural pauses)

| Time | On screen | Say (conversational) |
|------|-----------|----------------------|
| 0:00–0:04 | Title | Hey Sebastian — just wanted to quickly show you what we meant with the floor-plan stuff. |
| 0:04–0:10 | Steps / upload | So basically, you start with a normal 2D drawing — the kind of plan you’d already have for a building. |
| 0:10–0:15 | Apartment source | I’m using a furnished apartment plan here. |
| 0:15–0:22 | Detected apartment | Then we run detection. These boxes are what the model finds — doors, windows, bed, sofa, tables — marked on the plan. |
| 0:22–0:28 | Compare | Side by side helps: left is the original drawing, right is after detection. |
| 0:28–0:34 | Unit B source + detected | Same thing on a CAD plan — cleaner line drawing, still gets openings and furniture inventory. |
| 0:34–0:42 | Close | And the point is you don’t only get a pretty overlay — you get structured data: object list, rooms, JSON. Useful for building and energy workflows. |
| 0:42–0:48 | Hold close | That’s it — plan in, structured data out. Happy to test on a real Pribitzer drawing if useful. |

---

## Even more casual (if LinkedIn voice note + video)

Hey Sebastian, quick one.

Remember I mentioned floor-plan AI? This is what that looks like in practice.

You upload a 2D plan…  
run detection…  
and you get the rooms and furniture boxed out.

Here — apartment plan before and after.  
And here’s a CAD one too.

End result is structured data, not just screenshots.  
Figured that might be relevant for the energy / building-data side. Let me know if you want to try a real plan.

---

## German — human / explanatory

Hey Sebastian — ich wollte dir kurz zeigen, was wir mit dem Floor-Plan-Thema meinen.

Du startest mit einem normalen 2D-Grundriss — so wie ihr ihn eh schon habt.  
Hier zum Beispiel ein möbliertes Wohnungsbeispiel.

Dann läuft die Erkennung.  
Was du jetzt siehst, sind die erkannten Objekte — Türen, Fenster, Möbel wie Bett, Sofa, Tische — direkt auf dem Plan markiert.

Links Original, rechts nach der Detektion. So sieht man den Unterschied am klarsten.

Das funktioniert auch bei CAD-Plänen, nicht nur bei diesen Interior-Zeichnungen.

Und wichtig: Am Ende kommt nicht nur ein Bild raus, sondern strukturierte Daten — Objektliste, Räume, JSON.  
Das kann man weiterverwenden, z. B. in Building-Data- oder Energieausweis-Prozessen.

Kurz gesagt: Plan rein, strukturierte Daten raus.  
Wenn du willst, können wir das als Nächstes an einem echten Pribitzer-Plan testen.

---

## Delivery tips (so it sounds human)

- Smile slightly when you say “just wanted to quickly show you” — keeps it light  
- Pause half a beat after “run detection” so the boxes can land visually  
- Don’t rush the compare line — that’s the “aha” moment  
- Say “structured data” plainly; don’t say “leverage AI synergies”  
- If you stumble, keep going — explanatory > perfect

---

## LinkedIn caption (matches this tone)

Hey Sebastian — quick walkthrough of the floor-plan detection flow I mentioned.

You upload a 2D plan, the model marks openings + furniture, and you get structured output (inventory / rooms / JSON) — not just an annotated image.

Happy to try it on a real Pribitzer drawing if that’s useful.
