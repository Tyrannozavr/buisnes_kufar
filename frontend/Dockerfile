FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN rm -rf ./.output ./.nuxt

EXPOSE 3000

RUN npm run build
CMD [ "npm", "run", "start" ]