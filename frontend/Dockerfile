FROM node:23-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy prisma schema and generate client
COPY prisma ./prisma/
RUN npx prisma generate

# Copy rest of app and build
COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]