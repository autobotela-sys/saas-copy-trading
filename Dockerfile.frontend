# Multi-stage build for frontend from subdirectory
FROM node:20-alpine AS builder

WORKDIR /app

# Copy frontend package files
COPY frontend/package*.json ./
COPY frontend/next.config.ts ./
COPY frontend/tsconfig.json ./
COPY frontend/eslint.config.mjs ./
COPY frontend/postcss.config.mjs ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/app ./app
COPY frontend/components ./components
COPY frontend/lib ./lib
COPY frontend/hooks ./hooks
COPY frontend/public ./public

# Build
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
