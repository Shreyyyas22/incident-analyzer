# Stage 1: Build
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Development (default)
FROM node:20-slim
WORKDIR /app
COPY --from=builder /app ./
# Expose Vite's dev port
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
