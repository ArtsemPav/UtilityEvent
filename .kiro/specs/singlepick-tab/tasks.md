# Implementation Plan: SinglePick Tab

## Overview

Реализация вкладки "🎰 SinglePick" для создания, редактирования и экспорта JSON-конфигов по схеме SinglePick.
Работа ведётся послойно: сначала модели данных, затем валидатор, затем UI-виджеты, затем главная вкладка, и наконец — интеграция в `app.py`.
Язык реализации: **Python** (Streamlit-приложение).

## Tasks

- [x] 1. Создать модели данных в `models/singlepick.py`
  - Создать файл `models/singlepick.py`
  - Реализовать dataclass-иерархию, наследующую `Serializable` из `models/base.py`:
    - Типы наград: `FixedSPReward`, `RtpSPReward`, `PurchaseSPReward` (union `SPReward`)
    - Типы джекпотов: `FixedJackpot`, `CIJackpot`
    - Типы пиков: `RewardPick`, `JackpotPick`, `RetryPick` (union `Pick`)
    - `Wedge`, `PickersConfig`, `WheelConfig`, `ConfigSet`, `SinglePickConfig`
  - Реализовать `to_dict()` для каждой модели согласно схеме из design.md (PascalCase ключи, вложенные типовые ключи)
  - Реализовать `from_dict()` для каждой модели с корректным определением типа по ключу словаря
  - `SinglePickConfig.to_dict()` должен возвращать `{"ConfigSets": {...}}`
  - `SinglePickConfig.from_dict()` должен выбрасывать `ValueError` при отсутствии ключа `ConfigSets`
  - _Requirements: 9.2, 10.2, 10.3_

  - [ ]* 1.1 Написать unit-тесты для моделей (`tests/test_singlepick_models.py`)
    - Тест сериализации `RewardPick` с `FixedSPReward` → конкретный ожидаемый словарь
    - Тест сериализации `JackpotPick` с `CIJackpot` → конкретный ожидаемый словарь
    - Тест `SinglePickConfig.to_dict()` → корневой ключ `ConfigSets`
    - Тест `SinglePickConfig.from_dict()` с отсутствующим ключом `ConfigSets` → `ValueError`
    - Тест загрузки через `load_config_from_json` в кодировках UTF-8, UTF-8-BOM, CP1251
    - _Requirements: 9.2, 9.5, 10.2, 10.3_

  - [ ]* 1.2 Написать property-тест: round-trip сериализации (`tests/test_singlepick_properties.py`)
    - `# Feature: singlepick-tab, Property 2: Сериализация round-trip`
    - `@given` стратегия генерирует валидные объекты `SinglePickConfig` через `hypothesis.strategies`
    - Проверить: `SinglePickConfig.from_dict(config.to_dict()) == config`
    - `@settings(max_examples=100)`
    - **Property 2: Round-trip сериализации**
    - **Validates: Requirements 9.2, 10.2**

  - [ ]* 1.3 Написать property-тест: корневой ключ экспорта (`tests/test_singlepick_properties.py`)
    - `# Feature: singlepick-tab, Property 3: Корневой ключ экспорта`
    - `@given` генерирует `SinglePickConfig` с ≥ 1 ConfigSet
    - Проверить: `"ConfigSets" in config.to_dict()` и все имена ConfigSet-ов присутствуют в результате
    - `@settings(max_examples=100)`
    - **Property 3: Корневой ключ экспорта**
    - **Validates: Requirements 10.2, 10.3**

- [x] 2. Создать валидатор `services/singlepick_validator.py`
  - Создать файл `services/singlepick_validator.py`
  - Реализовать dataclass `ValidationError(configset_name: str, field: str, message: str)`
  - Реализовать функцию `validate_singlepick(config: SinglePickConfig) -> list[ValidationError]`
  - Проверки:
    - Имена ConfigSet-ов непусты и уникальны
    - Каждый `PickersConfig` содержит ≥ 1 пик в `picks`
    - Каждый `WheelConfig` содержит ≥ 1 сектор в `wedges`
    - В каждом `JackpotPick`: `min <= max` для `FixedJackpot` и `CIJackpot`
    - В каждом `RtpSPReward`: `percentage` кратно 0.01 с допуском 1e-9
  - _Requirements: 2.2, 2.3, 4.3, 5.5, 6.5, 8.2, 11.1, 11.2, 11.3_

  - [ ]* 2.1 Написать unit-тесты для валидатора (`tests/test_singlepick_validator.py`)
    - Тест: пустое имя ConfigSet → ошибка
    - Тест: дублирующееся имя ConfigSet → ошибка
    - Тест: пустой список `picks` → ошибка
    - Тест: пустой список `wedges` → ошибка
    - Тест: `min > max` в `FixedJackpot` → ошибка
    - Тест: `min > max` в `CIJackpot` → ошибка
    - Тест: `percentage = 0.015` (не кратно 0.01) → ошибка
    - Тест: валидный конфиг → пустой список ошибок
    - _Requirements: 2.2, 2.3, 4.3, 5.5, 6.5, 8.2, 11.1–11.3_

  - [ ]* 2.2 Написать property-тест: валидация имени ConfigSet (`tests/test_singlepick_properties.py`)
    - `# Feature: singlepick-tab, Property 1: Валидация имени ConfigSet`
    - `@given(existing_names=st.lists(st.text(min_size=1), unique=True), new_name=st.text())`
    - Проверить: пустая строка → ошибка; имя из `existing_names` → ошибка; непустое уникальное имя → нет ошибки
    - `@settings(max_examples=100)`
    - **Property 1: Валидация имени ConfigSet**
    - **Validates: Requirements 2.2, 2.3**

  - [ ]* 2.3 Написать property-тест: валидация Min/Max джекпота (`tests/test_singlepick_properties.py`)
    - `# Feature: singlepick-tab, Property 4: Валидация Min/Max в джекпоте`
    - `@given(min_val=st.integers(min_value=0), max_val=st.integers(min_value=0))`
    - Проверить: `min_val > max_val` → ошибка валидатора; `min_val <= max_val` → нет ошибки
    - `@settings(max_examples=100)`
    - **Property 4: Валидация Min/Max в джекпоте**
    - **Validates: Requirements 6.5**

  - [ ]* 2.4 Написать property-тест: валидация Percentage в RtpReward (`tests/test_singlepick_properties.py`)
    - `# Feature: singlepick-tab, Property 5: Валидация Percentage в RtpReward`
    - `@given(percentage=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))`
    - Проверить: `round(percentage / 0.01) * 0.01 != percentage` (с допуском 1e-9) → ошибка; кратное 0.01 → нет ошибки
    - `@settings(max_examples=100)`
    - **Property 5: Валидация Percentage в RtpReward**
    - **Validates: Requirements 5.5**

  - [ ]* 2.5 Написать property-тест: валидация непустых списков Picks/Wedges (`tests/test_singlepick_properties.py`)
    - `# Feature: singlepick-tab, Property 6: Валидация непустых списков`
    - `@given` генерирует `SinglePickConfig` с произвольными (в т.ч. пустыми) списками `picks`/`wedges`
    - Проверить: пустой список → ошибка; непустой → нет ошибки для этого поля
    - `@settings(max_examples=100)`
    - **Property 6: Валидация непустых списков Picks и Wedges**
    - **Validates: Requirements 4.3, 8.2, 11.2, 11.3**

- [x] 3. Checkpoint — убедиться, что все тесты проходят
  - Убедиться, что все тесты в `tests/test_singlepick_models.py`, `tests/test_singlepick_validator.py` и `tests/test_singlepick_properties.py` проходят. Задать вопросы пользователю при необходимости.

- [x] 4. Создать виджет наград `ui/widgets/singlepick_reward_widget.py`
  - Создать файл `ui/widgets/singlepick_reward_widget.py`
  - Реализовать функцию `render_sp_reward_widget(prefix: str, index: int, existing: Optional[SPReward] = None) -> SPReward`
  - Поддержать три типа наград: `FixedSPReward`, `RtpSPReward`, `PurchaseSPReward`
  - Для `FixedSPReward`: поля `Currency` (text_input) и `Amount` (number_input, int ≥ 0)
  - Для `RtpSPReward`: поля `Currency`, `Percentage` (float, step=0.01), `Min` (int ≥ 0), `Max` (int ≥ 0)
  - Для `PurchaseSPReward`: поле `ShopType` (text_input)
  - Все ключи `st.session_state` виджета использовать с переданным `prefix` и `index` для уникальности
  - _Requirements: 5.2, 5.3, 5.4, 7.2, 8.4_

- [x] 5. Создать главную вкладку `ui/tabs/singlepick_tab.py`
  - Создать файл `ui/tabs/singlepick_tab.py`
  - Реализовать `SinglePickState` (dataclass) и `get_singlepick_state()` согласно design.md
  - Реализовать `render_singlepick_tab()` как точку входа

  - [x] 5.1 Реализовать тулбар (`_render_toolbar`)
    - Кнопка "🆕 Новый конфиг": сброс состояния с подтверждением, если есть ConfigSet-ы
    - Загрузчик файла `st.file_uploader` (`.json`): вызов `load_config_from_json`, затем `SinglePickConfig.from_dict`; обработка `ValueError` и `Exception` через `st.error`; при успехе — `st.success` с количеством ConfigSet-ов
    - Счётчик `st.info(f"ConfigSet-ов: {N}")`
    - Все ключи session_state с префиксом `singlepick_`
    - _Requirements: 1.3, 9.1, 9.2, 9.3, 9.4, 9.5, 12.1, 12.2, 12.3_

  - [x] 5.2 Реализовать список ConfigSet-ов (`_render_configset_list`)
    - Отображать список всех ConfigSet-ов с именем и типом (Pickers / Wheel)
    - Кнопка ✏️ — выбрать ConfigSet для редактирования (установить `selected_configset_name`)
    - Кнопка 🗑️ — запросить подтверждение удаления через `confirm_delete_name`; при подтверждении удалить из `config.config_sets`
    - Кнопка "➕ Добавить ConfigSet" — открыть форму создания нового ConfigSet
    - _Requirements: 2.1, 2.4, 2.5, 2.6, 2.7_

  - [x] 5.3 Реализовать редактор ConfigSet (`_render_configset_editor`)
    - Поле ввода имени ConfigSet с валидацией (непустое, уникальное) через `st.error` inline
    - Radio-кнопки выбора типа: `Pickers` / `Wheel`; при смене типа для существующего ConfigSet — запрос подтверждения через `confirm_type_change`
    - Маршрутизация к `_render_pickers_editor()` или `_render_wheel_editor()` в зависимости от типа
    - _Requirements: 2.2, 2.3, 3.1, 3.2, 3.3_

  - [x] 5.4 Реализовать редактор Pickers (`_render_pickers_editor`)
    - Поля `TotalPickOnBoard` (number_input, int ≥ 1) и `PickUntilWin` (number_input, int ≥ 0)
    - Вызов `_render_pick_list()` для отображения и редактирования списка пиков
    - _Requirements: 4.1, 4.2_

  - [x] 5.5 Реализовать список пиков (`_render_pick_list`)
    - Отображать каждый пик с типом, Weight, PossibleMax и кратким описанием наград/джекпота
    - Кнопки ✏️ (раскрыть форму редактирования), ↑ / ↓ (переместить пик), 🗑️ (удалить)
    - Кнопка "➕ Добавить пик" с выбором типа: `RewardPick`, `JackpotPick`, `RetryPick`
    - Маршрутизация к `_render_reward_pick_form()`, `_render_jackpot_pick_form()`, `_render_retry_pick_form()`
    - _Requirements: 4.2, 4.4, 4.5_

  - [ ]* 5.6 Написать property-тест: перестановка пиков (`tests/test_singlepick_properties.py`)
    - `# Feature: singlepick-tab, Property 7: Перестановка пиков`
    - `@given(picks=st.lists(st.integers(), min_size=2), idx=st.integers(min_value=1))`
    - Тестировать вспомогательную функцию перемещения пика вверх (извлечь её в чистую функцию)
    - Проверить: элементы `i` и `i-1` поменялись местами, остальные не изменились, длина списка не изменилась
    - `@settings(max_examples=100)`
    - **Property 7: Перестановка пиков**
    - **Validates: Requirements 4.4**

  - [x] 5.7 Реализовать формы пиков
    - `_render_reward_pick_form()`: поля `Weight` (int ≥ 0), `PossibleMax` (int ≥ 0), список наград через `render_sp_reward_widget`; кнопки добавления/удаления наград
    - `_render_jackpot_pick_form()`: поля `Weight`, `PossibleMax`; radio выбора типа джекпота (`FixedJackpot` / `CIJackpot`); поля `Min`, `Max` (и `CIMin`, `CIMax` для CIJackpot); inline `st.error` при `Min > Max`
    - `_render_retry_pick_form()`: поля `Weight`, `PossibleMax`; необязательный список наград через `render_sp_reward_widget`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2_

  - [x] 5.8 Реализовать редактор Wheel (`_render_wheel_editor`) и список секторов (`_render_wedge_list`)
    - Отображать каждый Wedge с Weight и кратким описанием наград
    - Кнопки ✏️ (раскрыть форму), 🗑️ (удалить)
    - Форма Wedge: поле `Weight` (int ≥ 0), список наград через `render_sp_reward_widget`
    - Кнопка "➕ Добавить сектор"
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 5.9 Реализовать панель экспорта (`_render_export_panel`)
    - Вызвать `validate_singlepick(state.config)` и отобразить каждую ошибку через `st.warning`
    - Если ошибок нет и ConfigSet-ов ≥ 1: сформировать JSON через `state.config.to_dict()` + `json.dumps(..., indent=4, ensure_ascii=False)`, отобразить в `st.code(..., language="json")`
    - Если ConfigSet-ов нет: `st.warning(...)`, кнопка скачивания деактивирована
    - Кнопка `st.download_button` с `disabled=has_errors or is_empty`, `file_name="SinglePickConfig.json"`
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1–11.5_

- [x] 6. Зарегистрировать вкладку в `app.py`
  - Добавить импорт: `from ui.tabs.singlepick_tab import render_singlepick_tab`
  - Добавить `"🎰 SinglePick"` в вызов `st.tabs([...])` после `"💾 Экспорт"`
  - Добавить блок `with tab_singlepick: render_singlepick_tab()`
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 7. Финальный checkpoint — убедиться, что все тесты проходят
  - Убедиться, что все тесты в `tests/` проходят. Задать вопросы пользователю при необходимости.

## Notes

- Задачи с `*` — опциональные (тесты), могут быть пропущены для ускорения MVP
- Каждая задача ссылается на конкретные требования для трассируемости
- Property-тесты используют библиотеку **Hypothesis** (`@settings(max_examples=100)`)
- Функция перемещения пика вверх/вниз должна быть вынесена как чистая функция (без side-effects) для тестируемости
- Все ключи `st.session_state`, создаваемые вкладкой, используют префикс `singlepick_`
- Загрузка файлов переиспользует `load_config_from_json` из `services/json_io.py`
