FROM node:20-alpine
WORKDIR /app

# Copy optional .npmrc to improve reliability and speed
# COPY .npmrc ./

# Copy package manifests first to leverage Docker cache
COPY package*.json ./

# Simple npm install without host network or buildx
RUN npm install --no-audit --no-fund

# Copy the rest of the source code
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
