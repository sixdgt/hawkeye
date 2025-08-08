FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy app source
COPY . .

# Change ownership of /app to node user
RUN chown -R node:node /app

# Switch to node user
USER node

# Expose Vite dev server port
EXPOSE 5173

CMD ["npm", "run", "dev"]