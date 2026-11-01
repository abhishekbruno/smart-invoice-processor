# Reference and performance findings

The supplied references show a near-black navy starfield with diffuse violet clouds, and a blue/violet plasma structure with curved filaments, bright local highlights and soft transparent falloff. They contain no typography, panels or navigation; those details must be adapted from the existing interface, not claimed as literal reference matches.

Source inspection before optimization identifies large fixed blurred header/sidebar surfaces, nested backdrop filters on panels and controls, blurred pseudo-elements and broad shadow transitions as likely compositing costs. The Canvas renderer already caps DPR and suspends offscreen. The shared atmosphere also updates transforms on scroll. These are hypotheses from source inspection, not measured causes or FPS results. Prior browser access was declined; that restriction remains in force unless explicitly reauthorized.

Optimize compositing first: remove nested blur, use restrained panel-only blur, disable large fixed-surface blur, and restrict atmosphere scroll tracking to Full mode. Balanced is the default explicit preset. Preserve native scrolling and the existing renderer.
