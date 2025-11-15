# K.I.T.T. Theme Design Guide

Design documentation for the Knight Rider-inspired K.I.T.T. theme in the Cocktail Mixer frontend.

## Design Philosophy

The interface is inspired by K.I.T.T. (Knight Industries Two Thousand) from the 1980s TV series Knight Rider, featuring:

- **Iconic Red Scanner**: Sweeping red line animation
- **Black Background**: Deep black with subtle red gradients
- **Glowing Elements**: Red glow effects on interactive elements
- **Monospace Font**: Computer-terminal aesthetic
- **Uppercase Text**: Bold, authoritative text style
- **Minimalist UI**: Focus on functionality

## Color Palette

```css
--kitt-red: #ff0000;        /* Primary red */
--kitt-dark-red: #cc0000;   /* Darker red for contrast */
--kitt-black: #000000;      /* Deep black background */
--kitt-gray: #1a1a1a;       /* Dark gray for panels */
--kitt-light-gray: #333333; /* Light gray for secondary elements */
--kitt-text: #ff0000;       /* Red text */
--kitt-glow: rgba(255, 0, 0, 0.5); /* Red glow effect */
```

## Key Visual Elements

### 1. Scanner Animation
The iconic K.I.T.T. scanner that sweeps across the screen:
- 3px height red line
- Gradient from transparent → red → transparent
- 3-second animation cycle
- Creates the classic "thinking" effect

### 2. Pulsing Logo
The K.I.T.T. logo features:
- Red circular indicator that pulses
- Glowing text shadow effect
- Alternating glow intensity
- Letter spacing for dramatic effect

### 3. Status Indicators
Small circular indicators showing system status:
- 8px diameter
- Blinking animation when active
- Gray when inactive
- Red glow effect when active

### 4. Button Design
Touch-optimized buttons with:
- 2px red border
- Minimum 44x44px touch target
- Hover effect: red background, black text
- Active state: slight scale down
- Box shadow with red glow
- Secondary buttons: gray border, less prominent

### 5. Card Components
Cocktail and pump cards feature:
- Dark gray background
- Red border (2px for available, 1px for secondary)
- Hover effect: lift with increased glow
- Available items: full red border
- Unavailable items: gray border, reduced opacity

### 6. Progress Bar
Mixing progress indicator:
- Dark gray background track
- Red gradient fill
- Red glow effect
- Centered percentage text
- Smooth transition animations

## Screen Layout

### Header (Fixed)
```
┌─────────────────────────────────────────────┐
│ ● K.I.T.T.                                  │
│   Cocktail Intelligence Transfer Terminal   │
└─────────────────────────────────────────────┘
```
- 50px height
- Logo with pulsing indicator
- Subtitle in smaller text
- Red bottom border with glow

### Main Content (Scrollable)
```
┌─────────────────────────────────────────────┐
│                                             │
│  [Cocktail List / Detail / Status Screen]  │
│                                             │
│                                             │
└─────────────────────────────────────────────┘
```
- Flexible height (fills available space)
- Vertical scrolling when needed
- Red scrollbar thumb

### Footer (Fixed)
```
┌─────────────────────────────────────────────┐
│ ● SYSTEM ONLINE    ● MIXING IN PROGRESS    │
└─────────────────────────────────────────────┘
```
- 30px height
- System status indicators
- Red top border
- Blinking indicators

## Screen-Specific Designs

### Cocktail List Screen
- 2-column grid layout
- Filter buttons at top (ALL / AVAILABLE)
- Cards show: name, taste, timing tags
- Unavailable items have gray border and badge
- Touch-optimized card size

### Cocktail Detail Screen
- Large cocktail name with glow
- Ingredient list with amounts
- Missing ingredients highlighted
- Size selection (SMALL/MEDIUM/LARGE)
- Prominent "MAKE IT" button with pulse animation
- Back button for navigation

### Status Screen
- Large system status title
- Current cocktail being mixed (if active)
- Animated progress bar
- Mixing animation (8 pulsing bars)
- Pump grid showing active pumps
- Active pumps highlighted with animation

## Animation Patterns

### Pulse Animation
Used for: Logo, buttons, status indicators
```css
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}
```

### Glow Animation
Used for: Text, indicators, borders
```css
@keyframes glow {
  from { text-shadow: 0 0 5px red, 0 0 10px red; }
  to { text-shadow: 0 0 10px red, 0 0 20px red, 0 0 30px red; }
}
```

### Blink Animation
Used for: Active indicators
```css
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
```

### Scan Animation
Used for: Background scanner effect
```css
@keyframes scan {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}
```

### Pump Pulse Animation
Used for: Active pumps during mixing
```css
@keyframes pump-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

## Typography

### Font Family
```css
font-family: 'Courier New', monospace;
```
Monospace font gives computer-terminal aesthetic

### Font Sizes (Optimized for 480x320)
- Logo: 20px
- Subtitle: 9px
- Title: 18px
- Section Title: 12px
- Body: 11-13px
- Tag/Badge: 8-9px
- Footer: 9px

### Letter Spacing
Generous letter spacing for dramatic effect:
- Logo: 4px
- Titles: 2-3px
- Body: 1px
- Tags: 0.5px

### Text Effects
- Glowing text shadows on important elements
- Uppercase for emphasis
- High contrast (red on black)

## Touch Optimization

### Target Sizes
All interactive elements meet or exceed 44x44px:
- Buttons: 44px+ height
- Cards: 80px+ height
- Tap zones properly sized

### Touch Feedback
- Hover effects (also triggered on touch)
- Active state (scale down on press)
- Disabled state (reduced opacity)
- Visual feedback within 100ms

### Gesture Support
- Vertical scrolling (main content)
- Tap/click for interactions
- No pinch/zoom (disabled)
- No swipe gestures

## Accessibility Considerations

### Contrast
- High contrast (red on black)
- Readable at small sizes
- Distinguishable states

### Touch Targets
- Minimum 44x44px
- Adequate spacing between targets
- Clear visual boundaries

### Feedback
- Visual feedback for all interactions
- Status indicators always visible
- Progress clearly communicated

### Text Readability
- Monospace font at appropriate sizes
- Adequate line height
- Clear hierarchy

## Responsive Behavior

The UI is **fixed at 480x320** - not responsive:
```css
body {
  width: 480px;
  height: 320px;
  overflow: hidden;
}
```

This ensures:
- Perfect fit on target hardware
- Predictable layout
- No unexpected scrolling
- Optimized touch targets

## Customization Guide

To customize the theme, edit `src/App.css`:

### Change Primary Color
```css
:root {
  --kitt-red: #00ff00;  /* Green instead of red */
  --kitt-dark-red: #00cc00;
  --kitt-glow: rgba(0, 255, 0, 0.5);
}
```

### Adjust Animation Speed
```css
.scanner-line {
  animation: scan 2s ease-in-out infinite;  /* Faster scan */
}

.logo-pulse {
  animation: pulse 1s ease-in-out infinite;  /* Faster pulse */
}
```

### Change Font
```css
body {
  font-family: 'Arial', sans-serif;  /* Different font */
}
```

### Modify Layout
```css
.cocktail-grid {
  grid-template-columns: repeat(3, 1fr);  /* 3 columns instead of 2 */
}
```

## Implementation Notes

### Framer Motion
Used for page transitions and complex animations:
- `AnimatePresence` for enter/exit animations
- `motion.div` for animated components
- Smooth 300ms transitions between screens

### CSS Variables
All theme colors defined as CSS variables for easy customization

### No External Dependencies
All visual effects use pure CSS - no images or external assets needed

### Performance
- Hardware-accelerated animations (transform, opacity)
- Minimal repaints
- Optimized for 60 FPS on Raspberry Pi 5

## Design Inspiration

The theme draws inspiration from:
1. **Knight Rider (1982-1986)**: Original K.I.T.T. dashboard
2. **Retro Computer Terminals**: 1980s CRT aesthetics
3. **Sci-Fi Interfaces**: Clean, futuristic design
4. **Automotive HUDs**: Dashboard-style layouts

## Future Enhancements

Potential additions to maintain the K.I.T.T. theme:
- Voice feedback (text-to-speech responses)
- Sound effects (K.I.T.T. beeps and alerts)
- More elaborate animations
- Additional scanner patterns
- Analog speedometer-style progress indicators
- Startup sequence animation
