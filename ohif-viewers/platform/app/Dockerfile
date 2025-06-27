FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
ENV NODE_ENV=development

# Explicitly install patch-package globally to avoid missing binary errors
RUN npm install -g patch-package && \
    npm install --legacy-peer-deps && \
    patch-package

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Use nginx to serve the built files
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 