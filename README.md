# GPT Desktop

Лёгкая Linux desktop-обёртка для `https://chatgpt.com` на `PySide6` + `Qt WebEngine`.

Приложение открывает ChatGPT в отдельном окне с кастомной шапкой, полупрозрачным интерфейсом и сохранением сессии между перезапусками.

## Возможности

- отдельное окно ChatGPT без браузерных вкладок;
- кастомная шапка окна (сворачивание, разворачивание, закрытие, `Always on top`);
- перетаскивание и изменение размера окна (frameless window);
- сохранение cookies/local storage через persistent профиль Qt WebEngine;
- внедрение кастомных стилей поверх страницы.

## Требования

- Linux;
- Python 3.10+;
- `pip`;
- системные зависимости, необходимые для `PySide6`/`Qt WebEngine` (обычно ставятся автоматически через пакетный менеджер и `pip`).

## Клонирование

```bash
git clone https://github.com/gil1ges/chat_desktop.git
cd chat_desktop
```

## Установка и запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Альтернативный запуск:

```bash
./run.sh
```

`run.sh` использует:
1. `./venv/bin/python`, если есть;
2. иначе `./.venv/bin/python`;
3. иначе системный `python3`.

## Проверка, что всё собрано корректно

Минимальная проверка:

```bash
python3 -m py_compile app/main.py main.py
```

Запуск smoke-теста:
1. Открой приложение командой `python main.py` или `./run.sh`.
2. Убедись, что загружается `chatgpt.com`.
3. Проверь кнопки шапки: `Always on top`, сворачивание, разворачивание, закрытие.
4. Проверь drag окна из заголовка и resize за края.

## Установка ярлыка в меню приложений

```bash
chmod +x install_linux_desktop.sh
./install_linux_desktop.sh
```

Скрипт:
- копирует `gpt-desktop.desktop` в `~/.local/share/applications`;
- копирует иконку в `~/.local/share/icons/hicolor/scalable/apps`;
- обновляет путь проекта внутри `.desktop`;
- делает ярлык исполняемым.

## Структура проекта

- `main.py` - точка входа;
- `app/main.py` - UI, окно и `Qt WebEngine`;
- `app/injected_style.py` - код внедряемых стилей;
- `run.sh` - быстрый запуск;
- `install_linux_desktop.sh` - установка ярлыка;
- `assets/` - иконка и статические файлы.

## Ограничения

- это не официальный клиент OpenAI;
- работа стилей зависит от текущей разметки `chatgpt.com` и может потребовать обновления после изменений на сайте;
- качество прозрачности/blur зависит от оконного менеджера и композитора Linux.
