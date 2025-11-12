# Use lightweight Node image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy only the files needed for build first (better caching)
COPY package*.json ./
RUN npm install --production

# Copy all static site files
COPY . .

# Railway will inject its own PORT; default to 3000
ENV PORT=3000
EXPOSE 3000

# Start the web server
CMD ["node", "server.js"]
