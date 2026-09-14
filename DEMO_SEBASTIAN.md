# Sebastian demo video

## Deliverable
- Video: `sebastian_floorplan_demo.mp4` (~33s)
- Also at: `data/demo_video/sebastian_floorplan_demo.mp4`

## What Sebastian should see (fixes the earlier reject)
1. Title — AI floor plan detection
2. Clear 3-step flow: upload → infer → review
3. **Furnished apartment plan** shown first
4. **Detection overlay** with doors / windows / furniture boxes
5. **Compare** original vs detected
6. Second CAD example (Unit B)
7. Close on structured building data

## LinkedIn / message draft

Hi Sebastian — following up with a short demo of the floor-plan CV flow.

It takes a 2D plan, detects openings + furniture, and returns structured inventory (useful input for energy / building-data workflows).

Happy to walk through a real Pribitzer drawing if useful.

## Optional live screen recording (45–60s)
If you want a fuller UI capture with OBS:

1. Open `http://127.0.0.1:8765`
2. Add **Furnished apartment plan** + **Residential Unit B**
3. Click **Run detection on queue**
4. Stay on **Compare**, zoom once on Detected side
5. Switch queue cards once
6. Scroll inventory briefly
7. Stop

Keep voiceover light: “upload plan → detect structure and furniture → structured output.”
