# DevOps Telegram Bot

Бот создан в рамках модуля DevOps во время стажировки PT_START.

## Getting Started

Чтобы начать работу с ботом Telegram, выполните следующие действия:

1. Склонируйте этот репозиторий:

    ```shell
    git clone https://github.com/quwie/devops_bot.git
    ```

2. Забилдите образы Docker:

    ```shell
    docker-compose build
    ```

3. Запустите контейнеры Docker:

    ```shell
    docker-compose up -d
    ```

4. Убедитесь, что бот Telegram работает:

    ```shell
    docker-compose ps
    ```

    You should see the bot container listed as "Up".