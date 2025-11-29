# 📝 Project Status Summary

**Date**: 2025-11-29

## 🏗️ Modularization Completed

- **Refactoring**: Converted single scripts into a structured package (`src/`).
- **New Structure**:
  - `src/crawler.py`: Reservation checking logic.
  - `src/notifier.py`: Telegram notification logic.
  - `src/config.py`: Configuration management.
  - `src/utils.py`: Helper functions.
  - `main.py`: Unified entry point with CLI support.
- **Backup**: Original files backed up in `backup_original/`.

## ℹ️ Usage

- Run: `python main.py`
- Run with args: `python main.py 자유 호계`
