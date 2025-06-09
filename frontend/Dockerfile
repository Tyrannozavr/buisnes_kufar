FROM node:24-alpine

WORKDIR /app

npm install -g pnpm

COPY ./package*.json ./

RUN pnpm install

COPY . .
RUN rm -rf ./.output
RUN rm -rf ./.nuxt

EXPOSE 3000

RUN npm run build
CMD [ "pnpm", "run", "start" ]