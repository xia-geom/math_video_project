# Photo retouches — maths capsule, 4 October 2026

Built-in **imagegen** was used for both object removals. Originals remain intact.
The full generated images were used only as paint sources: `export_retouches.cjs`
composites bounded object regions into the original decoded photograph. This
preserves original people, lettering and architecture outside the masks rather
than accepting a globally regenerated photograph. Zero RGB channel values
changed outside the applied masks; the foreground traffic-light pole is protected.

| Original | Final project asset | Native dimensions |
| --- | --- | --- |
| `redaction_sciences_2026.jpg` | `assets/uqam_promo/redaction_sciences_2026_no_red_bag.png` | 1500 × 1125 |
| `president_kennedy.jpg` | `assets/uqam_promo/president_kennedy_no_vehicles.png` | 2560 × 1706 |

Generated paint, applied masks, input/output hashes and local pixel verification
are under `dist/uqam_revision_20261004/photo_edits/`. Only the source recipe and
provenance are committed; images are delivered separately with the film.

## Prompt 1 — library

Use case: precise-object-edit. Edit the supplied real photograph for a UQAM video.
Remove only the large bright red soft bag lying on the gray striped carpet at
the lower-right edge. Reconstruct that small patch with continuous matching
ribbed gray carpet and retain the adjacent black objects and chair legs.
Preserve the original composition, framing, lighting, colors and photographic
texture. All people, faces, hair, hands, clothing, laptops, furniture, windows,
walls, signs and every other pixel region should remain unchanged. Do not
beautify faces, alter facial features, add objects, crop, blur or add text.
Deliver the same 4:3 image composition at high resolution.

## Prompt 2 — campus

Use case: precise-object-edit. Edit target: this original UQAM Président-Kennedy
exterior photograph. Remove every truck and car, including the large dump truck
in the lower left, adjacent white car, dark car at lower center-right, dark car
farther right and all small distant cars/trucks on either side of the avenue.
Reconstruct only those vehicle-covered patches as the same road pavement, road
markings, sidewalk and background surfaces, matching photographic perspective,
sun/shadows and texture. All pedestrians and cyclists must remain in their exact
original positions, with original appearance. Preserve all architecture, UQAM
lettering, windows, traffic lights and signal colors, lampposts, trees, clouds,
sky, exhibition panels, signs and framing unchanged. Do not crop, redesign
streets, move people, sharpen faces, add/remove anything else or change global
color/lighting. High resolution 3:2 composition identical to original.

## Edge refinements

Two additional built-in edits used close crops of the left and right street
edges. Their generated patches replace only the corresponding vehicle masks;
foreground poles, cyclist and walking people are protected with original pixels.

Left-crop prompt: Precise-object-edit of this cropped street photograph. Remove
ALL the parked cars visible at the left edge under the trees: the silver rear
of the car, dark car next to it, every roof, bumper, wheel and car reflection.
Replace the car-covered area with an EMPTY continuation of the shaded gray
pavement and the same background fence/sidewalk. There must be absolutely no
vehicle or partial vehicle left anywhere in this small crop. Keep the foreground
diagonal black lamp post, its signs, background tree, red building, road markings,
people and crop geometry unchanged. No new objects. The result is a clean
realistic photograph of this exact street corner with no parked cars.

Right-crop prompt: Precise-object-edit of this cropped real street photograph.
Remove EVERY car visible: large dark car on the left road, small car just left
of the cyclist, dark distant car centered between the street posts, and
white/silver car directly behind the two walking people at the right. Remove
every visible bumper, roof, wheel and reflection, with no remaining vehicle
fragments. Reconstruct the empty shaded street, sidewalk and fence behind them
in their exact perspective. Preserve the cyclist, both walking people and all
other people, all lampposts/signs/posts, architecture, trees, road and bike-lane
markings, camera geometry and crop exactly as they are. Do not redesign or
beautify; only the cars disappear. No trucks, buses, vans or cars may remain.

## Provenance and reproduction

Sources, photographer/institution credits, original lineage and edited hashes
are registered in `assets/uqam_promo/sources.json`. The opening image is an
architecture/formula composite, not a posed research group. The selected smiling
steps photo comes from UQAM FSPD; no individual photographer is identified.
The 256 × 144 nighttime image was excluded from the HD render.

The edited PNGs are local derivatives, deliberately not fetched from their
original JPEG URLs. A fresh checkout must receive these exact reviewed assets
from the separate delivery before rendering; missing assets remain a real gate.
