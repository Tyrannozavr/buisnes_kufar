FROM node:24-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY ./package*.json ./

RUN pnpm install

COPY . .
RUN rm -rf ./.output
RUN rm -rf ./.nuxt

EXPOSE 3000

RUN pnpm run build
CMD [ "pnpm", "run", "start" ]