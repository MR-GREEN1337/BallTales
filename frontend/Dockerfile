FROM node:18-alpine AS base

# Dependencies stage
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Builder stage
FROM base AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Generate Prisma client
COPY prisma ./prisma/
RUN npx prisma generate

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Build the app
RUN npm run build

# Runner stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy public files
COPY --from=builder /app/public ./public

# Set up .next directory
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy Prisma files and generate client
COPY --from=builder --chown=nextjs:nodejs /app/prisma ./prisma
COPY --from=builder --chown=nextjs:nodejs /app/node_modules/.prisma ./node_modules/.prisma

USER nextjs

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]