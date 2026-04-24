# Requirements Document

## Introduction

Добавление новой вкладки "🎰 SinglePick" в существующее Streamlit-приложение "LiveEvent JSON Builder".
Вкладка предназначена для создания, редактирования и экспорта JSON-файлов конфигурации по схеме SinglePick.

Схема SinglePick описывает набор конфигурационных сетов (`ConfigSets`), каждый из которых содержит
один именованный объект типа `Pickers` (набор пиков с весами и наградами) или `Wheel` (колесо с секторами).
Вкладка должна полностью покрывать создание таких конфигов через UI без ручного редактирования JSON.

## Glossary

- **SinglePick_Tab**: Новая вкладка "🎰 SinglePick" в приложении.
- **ConfigSet**: Именованный объект верхнего уровня внутри `ConfigSets`; содержит ровно один дочерний объект — `Pickers` или `Wheel`.
- **Pickers**: Объект конфигурации пиков; содержит список `Picks`, `TotalPickOnBoard` и `PickUntilWin`.
- **Wheel**: Объект конфигурации колеса; содержит список `Wedges`.
- **Pick**: Один элемент списка `Picks`; является ровно одним из трёх типов: `RewardPick`, `JackpotPick`, `RetryPick`.
- **RewardPick**: Пик с наградой; содержит список `Reward`, `Weight` и `PossibleMax`.
- **JackpotPick**: Пик с джекпотом; содержит `Weight`, `PossibleMax` и ровно один из двух вариантов джекпота: `FixedJackpot` или `CIJackpot`.
- **RetryPick**: Пик-повтор; содержит `Weight` и `PossibleMax`; может содержать необязательный список `Reward`.
- **FixedReward**: Тип награды с фиксированной суммой; содержит `Currency` (строка) и `Amount` (целое число).
- **RtpReward**: Тип награды на основе RTP; содержит `Currency`, `Percentage` (кратно 0.01), `Min` и `Max`.
- **PurchaseReward**: Тип награды-покупки; содержит `ShopType` (строка).
- **FixedJackpot**: Вариант джекпота с фиксированными границами; содержит `Min`, `Max`, `PossibleMax`, `Weight`.
- **CIJackpot**: Вариант джекпота с CI-параметрами; содержит `Min`, `Max`, `CIMin`, `CIMax`, `PossibleMax`, `Weight`.
- **Wedge**: Один сектор колеса `Wheel`; содержит `Reward` и `Weight`.
- **SinglePick_State**: Изолированное состояние вкладки SinglePick, хранящееся в `st.session_state`.
- **JSON_Builder**: Сервис сборки итогового JSON из состояния SinglePick_State.
- **Validator**: Компонент проверки корректности данных перед экспортом.

---

## Requirements

### Requirement 1: Регистрация вкладки в приложении

**User Story:** Как пользователь приложения, я хочу видеть вкладку "🎰 SinglePick" рядом с существующими вкладками, чтобы переключаться между редактором LiveEvent и редактором SinglePick без перезагрузки страницы.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL отображаться в списке вкладок приложения после вкладки "💾 Экспорт".
2. WHEN пользователь переключается на вкладку "🎰 SinglePick", THE SinglePick_Tab SHALL отображать свой интерфейс без влияния на состояние вкладок "✏️ Редактор" и "💾 Экспорт".
3. THE SinglePick_Tab SHALL хранить своё состояние в изолированном ключе `st.session_state`, не пересекающемся с ключами других вкладок.

---

### Requirement 2: Управление ConfigSet-ами

**User Story:** Как конфигуратор, я хочу создавать, переименовывать, дублировать и удалять именованные ConfigSet-ы, чтобы формировать структуру `ConfigSets` итогового JSON.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL позволять добавлять новый ConfigSet с уникальным именем.
2. WHEN пользователь вводит имя ConfigSet, THE Validator SHALL проверять, что имя не пустое и не дублирует существующие имена в текущем конфиге.
3. IF имя ConfigSet уже существует в текущем конфиге, THEN THE Validator SHALL отображать сообщение об ошибке и блокировать сохранение.
4. THE SinglePick_Tab SHALL позволять переименовывать существующий ConfigSet.
5. THE SinglePick_Tab SHALL позволять дублировать ConfigSet; копия вставляется сразу после оригинала с уникальным именем (суффикс `_copy`, `_copy2`, ...).
6. THE SinglePick_Tab SHALL позволять удалять ConfigSet с подтверждением действия.
7. WHEN ConfigSet удалён, THE SinglePick_State SHALL немедленно отражать изменение без перезагрузки страницы.
8. THE SinglePick_Tab SHALL отображать список всех ConfigSet-ов с указанием их типа (Pickers / Wheel).

---

### Requirement 3: Выбор типа ConfigSet

**User Story:** Как конфигуратор, я хочу выбирать тип содержимого ConfigSet (Pickers или Wheel), чтобы задавать нужную структуру конфига.

#### Acceptance Criteria

1. WHEN создаётся новый ConfigSet, THE SinglePick_Tab SHALL предлагать выбор типа: `Pickers` или `Wheel`.
2. THE SinglePick_Tab SHALL отображать форму редактирования, соответствующую выбранному типу.
3. WHEN тип ConfigSet изменяется для существующего ConfigSet, THE SinglePick_Tab SHALL запрашивать подтверждение, так как это приведёт к потере текущих данных.

---

### Requirement 4: Редактирование Pickers

**User Story:** Как конфигуратор, я хочу задавать параметры Pickers (список пиков, TotalPickOnBoard, PickUntilWin), чтобы описывать логику выбора наград.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL предоставлять поля ввода для `TotalPickOnBoard` (целое число ≥ 1) и `PickUntilWin` (целое число ≥ 0).
2. THE SinglePick_Tab SHALL отображать список пиков (`Picks`) с возможностью добавления, редактирования и удаления каждого пика.
3. WHEN список `Picks` пуст, THE Validator SHALL отображать предупреждение, что требуется хотя бы один пик.
4. THE SinglePick_Tab SHALL позволять задавать порядок пиков в списке через перемещение вверх/вниз.
5. WHEN пользователь добавляет пик, THE SinglePick_Tab SHALL предлагать выбор типа: `RewardPick`, `JackpotPick` или `RetryPick`.

---

### Requirement 5: Редактирование RewardPick

**User Story:** Как конфигуратор, я хочу задавать параметры RewardPick (список наград, Weight, PossibleMax), чтобы описывать пики с конкретными наградами.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL предоставлять поля ввода для `Weight` (целое число ≥ 0) и `PossibleMax` (целое число ≥ 0) для RewardPick.
2. THE SinglePick_Tab SHALL позволять добавлять один или несколько объектов `Reward` в список `Reward` RewardPick.
3. WHEN добавляется награда, THE SinglePick_Tab SHALL предлагать выбор типа: `FixedReward`, `RtpReward` или `PurchaseReward`.
4. THE SinglePick_Tab SHALL отображать форму для каждого типа награды согласно его полям (см. Glossary).
5. WHEN значение `Percentage` в RtpReward не кратно 0.01, THE Validator SHALL отображать сообщение об ошибке.
6. THE SinglePick_Tab SHALL позволять удалять отдельные награды из списка `Reward`.

---

### Requirement 6: Редактирование JackpotPick

**User Story:** Как конфигуратор, я хочу задавать параметры JackpotPick с выбором варианта джекпота (FixedJackpot или CIJackpot), чтобы описывать пики с джекпотными наградами.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL предоставлять поля ввода для `Weight` (целое число ≥ 0) и `PossibleMax` (целое число ≥ 0) для JackpotPick.
2. WHEN создаётся JackpotPick, THE SinglePick_Tab SHALL предлагать выбор варианта джекпота: `FixedJackpot` или `CIJackpot`.
3. WHERE выбран `FixedJackpot`, THE SinglePick_Tab SHALL отображать поля `Min` и `Max` (целые числа ≥ 0).
4. WHERE выбран `CIJackpot`, THE SinglePick_Tab SHALL отображать поля `Min`, `Max`, `CIMin`, `CIMax` (целые числа ≥ 0).
5. IF значение `Min` превышает значение `Max` в любом варианте джекпота, THEN THE Validator SHALL отображать сообщение об ошибке.

---

### Requirement 7: Редактирование RetryPick

**User Story:** Как конфигуратор, я хочу задавать параметры RetryPick (Weight, PossibleMax и необязательный список наград), чтобы описывать пики-повторы.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL предоставлять поля ввода для `Weight` (целое число ≥ 0) и `PossibleMax` (целое число ≥ 0) для RetryPick.
2. THE SinglePick_Tab SHALL позволять добавлять необязательный список `Reward` к RetryPick по тем же правилам, что и для RewardPick (Requirement 5).

---

### Requirement 8: Редактирование Wheel

**User Story:** Как конфигуратор, я хочу задавать параметры Wheel (список секторов Wedges), чтобы описывать конфигурацию колеса.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL отображать список секторов (`Wedges`) с возможностью добавления, редактирования и удаления каждого сектора.
2. WHEN список `Wedges` пуст, THE Validator SHALL отображать предупреждение, что требуется хотя бы один сектор.
3. THE SinglePick_Tab SHALL предоставлять поля ввода для `Weight` (целое число ≥ 0) и списка `Reward` для каждого Wedge.
4. THE SinglePick_Tab SHALL позволять задавать список наград для Wedge по тем же правилам, что и для RewardPick (Requirement 5).

---

### Requirement 9: Загрузка существующего SinglePick JSON

**User Story:** Как конфигуратор, я хочу загружать существующий SinglePick JSON-файл в редактор, чтобы редактировать уже созданные конфиги.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL предоставлять элемент загрузки файла формата `.json`.
2. WHEN загружается файл, THE JSON_Builder SHALL разбирать его содержимое и заполнять SinglePick_State данными из файла.
3. IF загруженный файл не соответствует структуре схемы SinglePick (отсутствует ключ `ConfigSets`), THEN THE SinglePick_Tab SHALL отображать сообщение об ошибке и не изменять текущее состояние.
4. WHEN файл успешно загружен, THE SinglePick_Tab SHALL отображать количество загруженных ConfigSet-ов.
5. THE JSON_Builder SHALL корректно разбирать файлы в кодировках UTF-8, UTF-8-BOM и CP1251 (аналогично существующему `load_config_from_json`).

---

### Requirement 10: Экспорт SinglePick JSON

**User Story:** Как конфигуратор, я хочу скачивать итоговый JSON-файл SinglePick, чтобы использовать его в игровом проекте.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL предоставлять кнопку скачивания итогового JSON-файла.
2. WHEN пользователь нажимает кнопку скачивания, THE JSON_Builder SHALL формировать JSON с корневым ключом `ConfigSets`, содержащим все текущие ConfigSet-ы.
3. THE JSON_Builder SHALL форматировать итоговый JSON с отступами в 4 пробела и кодировкой UTF-8.
4. THE SinglePick_Tab SHALL отображать предпросмотр итогового JSON перед скачиванием.
5. WHEN в SinglePick_State нет ни одного ConfigSet, THE SinglePick_Tab SHALL отображать предупреждение и деактивировать кнопку скачивания.

---

### Requirement 11: Валидация перед экспортом

**User Story:** Как конфигуратор, я хочу получать сообщения об ошибках до скачивания файла, чтобы не экспортировать некорректный конфиг.

#### Acceptance Criteria

1. WHEN пользователь запрашивает предпросмотр или скачивание, THE Validator SHALL проверять, что каждый ConfigSet содержит ровно один дочерний объект (`Pickers` или `Wheel`).
2. WHEN пользователь запрашивает предпросмотр или скачивание, THE Validator SHALL проверять, что в каждом `Pickers` список `Picks` содержит не менее одного элемента.
3. WHEN пользователь запрашивает предпросмотр или скачивание, THE Validator SHALL проверять, что в каждом `Wheel` список `Wedges` содержит не менее одного элемента.
4. IF обнаружены ошибки валидации, THEN THE Validator SHALL отображать список всех ошибок с указанием имени ConfigSet и поля, в котором обнаружена ошибка.
5. IF обнаружены ошибки валидации, THEN THE SinglePick_Tab SHALL блокировать скачивание файла до их устранения.

---

### Requirement 12: Сброс состояния

**User Story:** Как конфигуратор, я хочу сбрасывать текущее состояние вкладки SinglePick, чтобы начать создание нового конфига с чистого листа.

#### Acceptance Criteria

1. THE SinglePick_Tab SHALL предоставлять кнопку "🆕 Новый конфиг", сбрасывающую SinglePick_State до пустого состояния.
2. WHEN пользователь нажимает кнопку сброса, THE SinglePick_Tab SHALL запрашивать подтверждение действия, если в SinglePick_State есть хотя бы один ConfigSet.
3. WHEN сброс подтверждён, THE SinglePick_State SHALL содержать пустой объект `ConfigSets` и не содержать выбранного ConfigSet.
