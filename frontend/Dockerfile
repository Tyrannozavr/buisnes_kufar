FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN yarn install

COPY . .
RUN rm -rf ./.output ./.nuxt

EXPOSE 3000

RUN yarn build
CMD [ "yarn", "start" ]