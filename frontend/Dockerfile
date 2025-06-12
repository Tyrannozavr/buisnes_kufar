FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN rm -rf ./.output ./.nuxt

EXPOSE 3000

RUN npm build
CMD [ "npm", "run", "start" ]