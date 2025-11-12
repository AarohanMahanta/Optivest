# -------------------------
# 1. Base image
# -------------------------
FROM node:18-alpine

# -------------------------
# 2. Set working directory
# -------------------------
WORKDIR /app

# -------------------------
# 3. Copy package files (if they exist)
# -------------------------
COPY package*.json ./

# -------------------------
# 4. Install dependencies
# -------------------------
RUN npm install

# -------------------------
# 5. Copy the rest of the app
# -------------------------
COPY . .

# -------------------------
# 6. Expose the Railway port
# -------------------------
ENV PORT=3000
EXPOSE 3000

# -------------------------
# 7. Start the Express server
# -------------------------
CMD ["npm", "start"]
