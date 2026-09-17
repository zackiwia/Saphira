# Saphira Animation Assets

Saphira uses prepared animation files rather than manipulating
individual body layers.

## Preferred format

Use numbered transparent PNG frames:

assets/animations/thinking/001.png
assets/animations/thinking/002.png
assets/animations/thinking/003.png

Frames are played in alphabetical order.

## Current animation slots

idle
thinking
talking
reaction
horn_dodge
opening

## Example

To create Saphira's thinking animation:

assets/animations/thinking/
    001.png
    002.png
    003.png
    004.png
    005.png

Then the existing behavior code can simply request:

self.play_animation("thinking")

The animation engine automatically discovers the files.

## Important

The existing reaction images remain unchanged:

neutral.png
happy.png
shocked.png

Do not rename those files.

## Recommended artwork

Transparent PNG frames are preferred.

Keep the character positioned consistently between frames so
the animation does not appear to jump around.

The animation engine does not redesign or modify artwork.

## Future animations

Additional animation slots can be added later for:

- blinking
- breathing
- thinking
- talking
- laughing
- surprised
- angry
- horn dodge
- opening
- walking
- sleeping
- waving
- picking up / being moved

Live2D remains a separate future renderer and is not required
by this system.
