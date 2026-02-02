# Zap Copy Trading - Frontend

Next.js frontend application for the Zap Copy Trading SaaS platform.

## Features

- **Authentication**: Login and registration with JWT tokens
- **User Dashboard**: Real-time P&L tracking, position management
- **Trading Profile**: Configure lot size multipliers and risk profiles
- **Broker Management**: Link Zerodha and Dhan accounts with OAuth token generation
- **Admin Dashboard**: User management and broadcast order execution
- **Real-time Updates**: Auto-refresh P&L and positions every 10 seconds
- **Token Countdown**: Visual countdown for token expiry

## Tech Stack

- **Next.js 16** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React Query** for data fetching and caching
- **React Hook Form** for form handling
- **Zustand** for state management (if needed)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:3445`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.local.example .env.local
```

3. Update `.env.local` with your API URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:3445
```

4. Run development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Auth pages (login, register)
│   ├── dashboard/         # User dashboard
│   ├── profile/           # Trading profile & broker account
│   ├── admin/             # Admin pages
│   └── layout.tsx         # Root layout
├── components/            # Reusable React components
│   ├── layout/           # Layout components (Sidebar, TopNavbar)
│   ├── ui/               # UI components (Button, Input, etc.)
│   └── forms/            # Form components
├── lib/                   # Utilities and API client
│   ├── api.ts            # API client functions
│   ├── auth.ts           # Authentication utilities
│   └── providers.tsx    # React Query provider
├── hooks/                 # Custom React hooks
│   └── useAuth.ts        # Authentication hook
└── public/               # Static assets
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:3445`)

## Deployment

### Railway Deployment

The frontend can be deployed to Railway as a separate service:

1. Connect your repository to Railway
2. Set the root directory to `saas_app/frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
4. Railway will automatically detect Next.js and deploy

### Build for Production

```bash
npm run build
npm start
```

## API Integration

All API calls are handled through `lib/api.ts`. The API client automatically:
- Adds JWT tokens to requests
- Handles errors
- Provides TypeScript types for all endpoints

## Authentication Flow

1. User logs in via `/login`
2. JWT token is stored in localStorage
3. Token is automatically included in all API requests
4. Protected routes check authentication via `useRequireAuth` hook
5. Admin routes use `useRequireAdmin` hook for role-based access

## Styling

The app uses Tailwind CSS with custom design tokens from Stitch:
- Primary color: `#0db9f2`
- Background light: `#f5f8f8`
- Background dark: `#101e22`
- Material Symbols icons for UI elements

## Development

- Run `npm run dev` for development server
- Run `npm run build` to build for production
- Run `npm run lint` to check code quality

## Notes

- Real-time updates use polling (10s interval) - can be upgraded to WebSockets later
- Token countdown updates every second
- All forms include validation using React Hook Form
- Error handling is implemented throughout the app
