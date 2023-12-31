# Описание
---
Foodgram это проект направленный на создание и распространение рецептов между пользователями. Понравившиеся рецепты можно добавить в корзину и скачать список покупок с ингридиентами для удобства.
#
# Деплой
---
При установленном Докере на сервере и внесёнными в папку foodgram/infra/ `docker-compose.yml` и `nginx.conf`, создать в репрезитории github ключи. 
| Key | Vale |
| --- | --- |
| DOCKER_PASSWORD | пароль докера |
| DOCKER_USERNAME | имя пользователя докера |
| HOST | ip сервера |
| SSH_KEY | ключ |
| SSH_PASSPHRASE | пароль ключа
| USER | имя пользователя сервера |
После успешного деплоя можно использовать команды для импорта ингредиентов:
```bash
sudo docker-compose exec backend python manage.py import_ingrdients --path <путь_к_ингрдиенты.csv>
```
```bash
sudo docker-compose exec -it backend python manage.py createsuperuser
```
На данном этапе проект должен уже работать и осталось только позволить пользователям наполнить его своими рецептами.
#
Проект можно найти [здесь](https://yaprtski.ddns.net)
#
### Автор
Владислав Коновалов :3