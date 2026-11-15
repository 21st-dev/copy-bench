"""The fixed checklist and v10 scoring weights, copied from the Copy Bench lab grader (scripts/grader/).
Each check is a statement about the copy; the judge answers same / minor / major / n/a."""

CHECKS = {
    "content": [
        ("c1", "all text of the original is present in the copy, with the same words"),
        ("c2", "all elements are present (buttons, icons, images, shapes, decorations)"),
        ("c3", "same counts of repeated things (cards, items, list rows, blades, dots)"),
        ("c4", "nothing extra was added"),
    ],
    "layout": [
        ("l1", "same blocks in the same order"),
        ("l2", "positions within ~5% of the viewport"),
        ("l3", "sizes within ~10%"),
        ("l4", "same alignment and overlap"),
        ("l5", "nothing cut off or overflowing that isn't in the original"),
    ],
    "color": [
        ("co1", "same background colour"),
        ("co2", "same accent colours (hue and lightness)"),
        ("co3", "same text and surface colours"),
        ("co4", "same gradients, direction and stops (n/a if the original has none)"),
        ("co5", "same light/dark relations and shadows"),
    ],
    "typography": [
        ("t1", "same family class (serif, sans, mono, display)"),
        ("t2", "same weight"),
        ("t3", "size within ~10%"),
        ("t4", "same case and letter spacing"),
        ("t5", "same line breaks"),
    ],
    "motion": [
        ("m1", "the same things move, and the same things stay still"),
        ("m2", "same kind of motion (slide, scale, rotate, fade, morph)"),
        ("m3", "same path and distance"),
        ("m4", "start time and speed within ~20% (compare positions at the same timestamps)"),
        ("m5", "same stagger, easing and loop (reverses, repeats or stops at the same moments)"),
        ("m6", "same reaction to mouse / scroll (n/a if no input in the capture)"),
        ("m7", "canvas / shader content: same structure over time (n/a if none)"),
    ],
}
STILL_CHECK = ("m0", "still where the original is still: nothing moves in the copy either")
WEIGHTS = {"content": 0.25, "layout": 0.25, "motion": 0.20, "color": 0.15, "typography": 0.15}
PENALTY = {"same": 0, "minor": 15, "major": 40}
