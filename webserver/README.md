# Logbook Web Client

SvelteKit-based web interface for the Logbook API.

## Features

- **Enlist**: Register as a new Scribe
- **Unlock/Lock**: Authenticate and secure your logbook
- **Profile Management**: View, amend, and retire your account
- **Entry Management**: Create, read, update, and delete entries
- **Chronicle**: View your documented journey

## Development

### Prerequisites

- Node.js 18+
- Logbook API server running on port 5000

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The web client runs on port 5173 and proxies API requests to the Flask backend on port 5000.

### Running Both Servers

From the project root, use Honcho to run both servers:

```bash
honcho start
```

This starts:
- **api**: Flask API server on port 5000
- **web**: SvelteKit dev server on port 5173

## Project Structure

```
webserver/
├── src/
│   ├── lib/
│   │   ├── api.ts           # API client for backend communication
│   │   └── stores/
│   │       └── auth.ts      # Authentication state store
│   └── routes/
│       ├── +layout.svelte   # Main layout with navigation
│       ├── +page.svelte     # Home page
│       ├── enlist/          # Registration page
│       ├── unlock/          # Login page
│       ├── profile/         # Profile management
│       ├── chronicle/       # Entry list
│       └── entries/
│           ├── new/         # Create entry
│           └── [id]/        # Edit entry
├── vite.config.ts           # Vite config with API proxy
└── package.json
```

## Building for Production

```bash
npm run build
npm run preview
```

Note: For production deployment, you may need to configure an appropriate [SvelteKit adapter](https://svelte.dev/docs/kit/adapters).
