```bash   
 sudo mkdir -p nginx/letsencrypt/live/tradesynergy.ru
 ```


```bash 
  sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048  -keyout nginx/letsencrypt/live/tradesynergy.ru/privkey.pem
 -out nginx/letsencrypt/live/tradesynergy.ru/fullchain.pem   -subj "/CN=tradesynergy.ru"
```

#  команда запускается из родительской для этой директории, создает фейковые сертификаты которые просто позволяют запустить nginx для выпуска настоящих, дальше 

```bash 
    docker compose up -d certbot
```