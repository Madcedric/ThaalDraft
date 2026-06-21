# ThaalDraft V2 UI/UX Guidelines

## Design Philosophy
The application must resemble a premium SaaS platform, drawing inspiration from Notion, Linear, Grammarly, and Overleaf. 
It must be clean, minimal, fast, and accessible. Generic admin dashboards and visual clutter must be avoided.

## Workspace Layout (Desktop)
A modern, hybrid workspace utilizing a 3-pane layout:
1. **Left Pane (Document Structure)**: Outline view, navigation, and section management.
2. **Center Pane (Live Manuscript)**: The main editor/viewer showing the reconstructed text or the formatted preview.
3. **Right Pane (Analysis Panel)**: Real-time insights, compliance reports, citation validation, and AI reviewer comments.

## Interactive Elements
- **No Dead Buttons**: Every action must be clickable and provide immediate feedback.
- **Live Status**: Progress bars or spinners must indicate background tasks (uploading, parsing, analyzing).
- **Error Handling**: Use inline toasts or contextual banners. No silent failures. Provide actionable recovery steps.

## Mobile & Tablet Support
- **Responsive Layout**: The 3-pane desktop view must collapse into a tabbed or drawer-based layout on smaller screens.
- **Touch-Friendly**: Buttons and interactive elements must have adequate touch targets (min 44x44px).

## Typography & Colors
- **Fonts**: Inter or similar modern sans-serif for UI, serif for manuscript preview.
- **Colors**: Monochromatic base with subtle primary accents (e.g., Indigo or Slate). Support for a dark mode is required.
