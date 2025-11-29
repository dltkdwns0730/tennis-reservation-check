# 📱 Telegram Bot Setup Guide

## 1. Create a Bot (BotFather)

1. Open Telegram and search for **`@BotFather`**.
2. Send command: `/newbot`
3. Enter a name for your bot (e.g., `Tennis Checker`).
4. Enter a username (must end in `bot`, e.g., `MyTennis_bot`).
5. Copy the **HTTP API Token**. This is your `TELEGRAM_BOT_TOKEN`.

## 2. Get Your Chat ID (UserInfoBot)

1. Search for **`@userinfobot`**.
2. Click **Start**.
3. Copy the `Id` number. This is your `TELEGRAM_CHAT_ID`.

## 3. Configure Project

1. Open `.env` file in the project folder.
2. Paste your values:

   ```ini
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=12345678
   ```

## 4. Activate Bot

1. Search for your new bot (the username you created in step 1).
2. Click **Start** to allow it to send you messages.
