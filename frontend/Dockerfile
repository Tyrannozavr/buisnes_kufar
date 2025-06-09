FROM node:24-slim

WORKDIR /app

COPY ./package*.json ./

RUN npm install

COPY . .
RUN rm -rf ./.output
RUN rm -rf ./.nuxt

EXPOSE 3000

RUN npm run build
CMD [ "npm", "run", "start" ]