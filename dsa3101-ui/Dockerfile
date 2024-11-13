FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

EXPOSE 3000

# Change to dev mode for now
CMD ["npm", "run", "dev"]