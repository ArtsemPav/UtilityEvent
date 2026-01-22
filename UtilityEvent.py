import sys
import json
import os
import copy
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class LiveEventBuilderGUI(QMainWindow):
    """Графический интерфейс для создания JSON файлов событий"""
    
    def __init__(self):
        super().__init__()
        self.events = []  # Список всех событий
        self.current_event_index = -1  # Индекс текущего события
        self.current_segment = None
        self.current_stage = None
        self.current_node = None
        self.current_goal = None
        self.current_reward_index = -1
        self.node_counter = 1
        self.stage_counter = 1
        self.goal_widgets = {}
        self.init_ui()
        
    @property
    def current_event(self):
        """Текущее выбранное событие"""
        if 0 <= self.current_event_index < len(self.events):
            return self.events[self.current_event_index]
        return None
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Live Event Builder v1.2 - Множественные сегменты')
        self.setGeometry(100, 100, 1400, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель - список событий и дерево структуры
        left_panel = QSplitter(Qt.Vertical)
        
        # Панель списка событий
        events_panel = QFrame()
        events_layout = QVBoxLayout(events_panel)
        events_layout.addWidget(QLabel("Events:"))
        
        # Список событий
        self.events_list = QListWidget()
        self.events_list.itemClicked.connect(self.on_event_selected)
        events_layout.addWidget(self.events_list)
        
        # Кнопки управления событиями
        events_buttons = QHBoxLayout()
        self.add_event_btn = QPushButton("+")
        self.add_event_btn.setToolTip("Add event")
        self.add_event_btn.clicked.connect(self.add_new_event)
        self.remove_event_btn = QPushButton("-")
        self.remove_event_btn.setToolTip("Delete event")
        self.remove_event_btn.clicked.connect(self.remove_current_event)
        self.duplicate_event_btn = QPushButton("Double")
        self.duplicate_event_btn.setToolTip("Duplicate event")
        self.duplicate_event_btn.clicked.connect(self.duplicate_current_event)
        events_buttons.addWidget(self.add_event_btn)
        events_buttons.addWidget(self.remove_event_btn)
        events_buttons.addWidget(self.duplicate_event_btn)
        events_buttons.addStretch()
        events_layout.addLayout(events_buttons)
        
        left_panel.addWidget(events_panel)
        
        # Дерево структуры текущего события
        structure_panel = QFrame()
        structure_layout = QVBoxLayout(structure_panel)
        structure_layout.addWidget(QLabel("Структура события:"))
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel('Детали события')
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        structure_layout.addWidget(self.tree_widget)
        
        left_panel.addWidget(structure_panel)
        left_panel.setSizes([200, 600])  # Сделали структуру события больше
        
        main_layout.addWidget(left_panel)
        
        # Правая панель - редактирование
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Панель инструментов
        toolbar = self.create_toolbar()
        right_layout.addWidget(toolbar)
        
        # Вкладки редактирования
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        right_layout.addWidget(self.tab_widget)
        
        # Кнопки действий
        button_panel = self.create_button_panel()
        right_layout.addWidget(button_panel)
        
        main_layout.addWidget(right_panel, 1)
        
        # Создаем вкладки
        self.create_event_tab()
        self.create_segment_tab()
        self.create_stage_tab()
        self.create_node_tab()
        self.create_goal_tab()
        self.create_reward_tab()
        
        # Статус бар
        self.statusBar().showMessage('Ready')
        
        # Создаем начальное событие
        self.create_new_event()
        
    def create_toolbar(self):
        """Создать панель инструментов"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # Кнопки действий
        new_file_action = QAction(QIcon.fromTheme('document-new'), 'New file', self)
        new_file_action.triggered.connect(self.create_new_file)
        toolbar.addAction(new_file_action)
        
        open_action = QAction(QIcon.fromTheme('document-open'), 'Open', self)
        open_action.triggered.connect(self.open_event_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(QIcon.fromTheme('document-save'), 'Save', self)
        save_action.triggered.connect(self.save_event_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        add_segment_action = QAction(QIcon.fromTheme('list-add'), 'Add Segment', self)
        add_segment_action.triggered.connect(self.add_segment)
        toolbar.addAction(add_segment_action)
        
        remove_segment_action = QAction(QIcon.fromTheme('list-remove'), 'Remove Segment', self)
        remove_segment_action.triggered.connect(self.remove_current_segment)
        toolbar.addAction(remove_segment_action)
        
        toolbar.addSeparator()
        
        add_stage_action = QAction(QIcon.fromTheme('list-add'), 'Add Stage', self)
        add_stage_action.triggered.connect(self.add_stage)
        # toolbar.addAction(add_stage_action)
        
        add_node_action = QAction(QIcon.fromTheme('list-add'), 'Add Node', self)
        add_node_action.triggered.connect(self.add_node_dialog)
        toolbar.addAction(add_node_action)
        
        add_goal_action = QAction(QIcon.fromTheme('list-add'), 'Add Goal', self)
        add_goal_action.triggered.connect(self.add_goal_dialog)
        toolbar.addAction(add_goal_action)
        
        return toolbar
    
    def create_button_panel(self):
        """Создать панель кнопок"""
        panel = QFrame()
        layout = QHBoxLayout(panel)
        
        self.validate_btn = QPushButton('Check all')
        self.validate_btn.clicked.connect(self.validate_all_events)
        layout.addWidget(self.validate_btn)
        
        self.export_btn = QPushButton('Export JSON')
        self.export_btn.clicked.connect(self.export_json)
        self.export_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        layout.addWidget(self.export_btn)
        
        return panel
    
    def create_event_tab(self):
        """Создать вкладку редактирования события"""
        self.event_tab = QWidget()
        layout = QFormLayout(self.event_tab)
        
        self.event_id_edit = QLineEdit()
        self.event_id_edit.setText("AncientDragonChallenge")
        layout.addRow("EventID:", self.event_id_edit)
        
        self.min_level = QSpinBox()
        self.min_level.setValue(70)
        layout.addRow("MinLevel:", self.min_level)
        
        self.event_bundle_path = QLineEdit()
        self.event_bundle_path.setText("_events/AncientDragonChallenge")
        layout.addRow("AssetBundlePath:", self.event_bundle_path)
        
        self.event_blocker_path = QLineEdit()
        self.event_blocker_path.setText("AncientDragonChallenge_Dialog")
        layout.addRow("BlockerPrefabPath:", self.event_blocker_path)
        
        self.event_node_path = QLineEdit()
        self.event_node_path.setText("AncientDragonChallenge_Dialog")
        layout.addRow("NodeCompletionPrefabPath:", self.event_node_path)
        
        self.event_roundel_path = QLineEdit()
        self.event_roundel_path.setText("Roundel/AncientDragonChallenge_Roundel")
        layout.addRow("RoundelPrefabPath:", self.event_roundel_path)
        
        self.event_event_card_path = QLineEdit()
        self.event_event_card_path.setText("EventCard/AncientDragonChallenge_EventCard")
        layout.addRow("EventCardPrefabPath:", self.event_event_card_path)
        
        self.event_content_key = QLineEdit()
        self.event_content_key.setText("AncientDragonChallenge")
        layout.addRow("ContentKey:", self.event_content_key)
        
        self.repeats = QSpinBox()
        self.repeats.setRange(-1, 100)
        self.repeats.setValue(-1)
        layout.addRow("NumberOfRepeats:", self.repeats)
         
        self.hide_roundel = QCheckBox()
        self.hide_roundel.setChecked(False)
        layout.addRow("IsRoundelHidden:", self.hide_roundel)
         
        self.show_roundel_on_all_machines = QCheckBox()
        self.show_roundel_on_all_machines.setChecked(True)
        layout.addRow("ShowRoundelOnAllMachines:", self.show_roundel_on_all_machines)
        
        self.is_currency_event_check = QCheckBox()
        self.is_currency_event_check.setChecked(False)
        layout.addRow("IsCurrencyEvent:", self.is_currency_event_check)
        
        self.starting_currency = QSpinBox()
        self.starting_currency.setValue(0)
        layout.addRow("StartingEventCurrency:", self.starting_currency)

        self.entry_types = QLineEdit()
        self.entry_types.setPlaceholderText("MegaSweeps, AriaSweepstakes")
        layout.addRow("EntryTypes:", self.entry_types)
        
        self.time_warning_edit = QDateTimeEdit()
        self.time_warning_edit.setDateTime(QDateTime.currentDateTime().addDays(14))
        self.time_warning_edit.setCalendarPopup(True)
        layout.addRow("TimeWarning:", self.time_warning_edit)
        
        self.tab_widget.addTab(self.event_tab, "Event")
        
        # Подключение сигналов
        self.event_id_edit.textChanged.connect(self.update_current_event)
        self.min_level.valueChanged.connect(self.update_current_event)
        self.event_bundle_path.textChanged.connect(self.update_current_event)
        self.event_blocker_path.textChanged.connect(self.update_current_event)
        self.event_node_path.textChanged.connect(self.update_current_event)
        self.event_roundel_path.textChanged.connect(self.update_current_event)
        self.event_event_card_path.textChanged.connect(self.update_current_event)
        self.event_content_key.textChanged.connect(self.update_current_event)
        self.repeats.valueChanged.connect(self.update_current_event)
        self.hide_roundel.stateChanged.connect(self.update_current_event)
        self.show_roundel_on_all_machines.stateChanged.connect(self.update_current_event)
        self.is_currency_event_check.stateChanged.connect(self.update_current_event)
        self.starting_currency.valueChanged.connect(self.update_current_event)
        self.entry_types.textChanged.connect(self.update_current_event)
        self.time_warning_edit.dateTimeChanged.connect(self.update_current_event)
    
    def create_segment_tab(self):
        """Создать вкладку редактирования сегмента"""
        self.segment_tab = QWidget()
        layout = QFormLayout(self.segment_tab)
        
        self.segment_name_edit = QLineEdit()
        self.segment_name_edit.setPlaceholderText("Segment_1")
        layout.addRow("Название сегмента:", self.segment_name_edit)
        
        # Диапазоны
        ranges_group = QGroupBox("Свойства сегмента")
        ranges_layout = QFormLayout()
        
        self.avg_wager_edit = QLineEdit()
        self.avg_wager_edit.setPlaceholderText("100-1000")
        ranges_layout.addRow("Average Wager Range:", self.avg_wager_edit)
        
        self.spinpad_edit = QLineEdit()
        self.spinpad_edit.setPlaceholderText("500-5000")
        ranges_layout.addRow("Spinpad Range:", self.spinpad_edit)
        
        self.level_edit = QLineEdit()
        self.level_edit.setPlaceholderText("15-50")
        ranges_layout.addRow("Level Range:", self.level_edit)
        
        self.vip_edit = QLineEdit()
        self.vip_edit.setText("0-10")
        ranges_layout.addRow("VIP Range:", self.vip_edit)
        
        ranges_group.setLayout(ranges_layout)
        layout.addRow(ranges_group)
        
        # Кнопки для управления сегментом
        segment_buttons = QHBoxLayout()
        self.save_segment_btn = QPushButton("Save")
        self.save_segment_btn.clicked.connect(self.update_segment_data)
        self.save_segment_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.duplicate_segment_btn = QPushButton("Duplicate")
        self.duplicate_segment_btn.clicked.connect(self.duplicate_current_segment)
        
        segment_buttons.addWidget(self.save_segment_btn)
        segment_buttons.addWidget(self.duplicate_segment_btn)
        segment_buttons.addStretch()
        
        layout.addRow(segment_buttons)
        
        self.tab_widget.addTab(self.segment_tab, "Segment")
        
        # Подключение сигналов
        self.segment_name_edit.textChanged.connect(self.update_segment_data)
        self.avg_wager_edit.textChanged.connect(self.update_segment_data)
        self.spinpad_edit.textChanged.connect(self.update_segment_data)
        self.level_edit.textChanged.connect(self.update_segment_data)
        self.vip_edit.textChanged.connect(self.update_segment_data)
    
    def create_stage_tab(self):
        """Создать вкладку редактирования этапа"""
        self.stage_tab = QWidget()
        layout = QFormLayout(self.stage_tab)
        
        self.stage_id_spin = QSpinBox()
        self.stage_id_spin.setRange(1, 100)
        self.stage_id_spin.valueChanged.connect(self.update_stage_data)
        layout.addRow("StageID:", self.stage_id_spin)
        
        # self.tab_widget.addTab(self.stage_tab, "Stage")
    
    def create_node_tab(self):
        """Создать вкладку редактирования узла"""
        self.node_tab = QWidget()
        layout = QFormLayout(self.node_tab)
    
        # Тип узла
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems(["ProgressNode", "EntriesNode", "EntriesProgressNode", "DummyNode"])
        self.node_type_combo.currentTextChanged.connect(self.on_node_type_changed)
        layout.addRow("Node:", self.node_type_combo)
        
        self.node_id_spin = QSpinBox()
        self.node_id_spin.setRange(1, 9999)
        self.node_id_spin.valueChanged.connect(self.update_node_data)
        layout.addRow("NodeID:", self.node_id_spin)
        
        self.next_node_id_spin = QLineEdit()
        self.next_node_id_spin.setPlaceholderText("Введите NextNodeID через запятую")
        self.next_node_id_spin.textChanged.connect(self.update_node_data)
        layout.addRow("Next Node ID:", self.next_node_id_spin)
               
        self.games_edit = QLineEdit()
        self.games_edit.setPlaceholderText("Введите названия игр через запятую, например: DragonTreasurePearls, Buffalo, WildAztec")
        self.games_edit.textChanged.connect(self.update_node_data)
        layout.addRow("Game list:", self.games_edit)
        
        examples_label = QLabel("Примеры: RomanTribune, TBMammothPower")
        examples_label.setStyleSheet("color: gray; font-size: 10px;")
        examples_label.setWordWrap(True)
        layout.addRow(examples_label)

        # MinBet с переключаемым интерфейсом
        minbet_group = QGroupBox("MinBet")
        minbet_layout = QVBoxLayout()
        
        self.minbet_type_combo = QComboBox()
        self.minbet_type_combo.addItems(["Фиксированная", "Переменная"])
        self.minbet_type_combo.currentTextChanged.connect(self.on_minbet_type_changed)
        minbet_layout.addWidget(QLabel("Тип ставки:"))
        minbet_layout.addWidget(self.minbet_type_combo)
        
        # Стековый виджет для переключения между типами MinBet
        self.minbet_stack = QStackedWidget()
        
        # Виджет для фиксированной ставки
        fixed_widget = QWidget()
        fixed_layout = QVBoxLayout(fixed_widget)
        
        self.minbet_fixed_spin = QDoubleSpinBox()
        self.minbet_fixed_spin.setRange(0, 1000000)
        self.minbet_fixed_spin.setValue(250000)
        self.minbet_fixed_spin.valueChanged.connect(self.update_node_data)
        fixed_layout.addWidget(QLabel("Значение (MinBet):"))
        fixed_layout.addWidget(self.minbet_fixed_spin)
        
        self.minbet_stack.addWidget(fixed_widget)
        
        # Виджет для переменной ставки
        variable_widget = QWidget()
        variable_layout = QFormLayout(variable_widget)
        
        self.minbet_variable_spin = QDoubleSpinBox()
        self.minbet_variable_spin.setRange(0, 10)
        self.minbet_variable_spin.setSingleStep(0.01)
        self.minbet_variable_spin.setValue(0.8)
        self.minbet_variable_spin.valueChanged.connect(self.update_node_data)
        variable_layout.addRow("Коэффициент (Variable):", self.minbet_variable_spin)
        
        self.minbet_min_spin = QDoubleSpinBox()
        self.minbet_min_spin.setRange(0, 1000000)
        self.minbet_min_spin.setValue(25000)
        self.minbet_min_spin.valueChanged.connect(self.update_node_data)
        variable_layout.addRow("Минимум (Min):", self.minbet_min_spin)
        
        self.minbet_max_spin = QDoubleSpinBox()
        self.minbet_max_spin.setRange(0, 10000000)
        self.minbet_max_spin.setValue(5000000)
        self.minbet_max_spin.valueChanged.connect(self.update_node_data)
        variable_layout.addRow("Максимум (Max):", self.minbet_max_spin)
        
        self.minbet_stack.addWidget(variable_widget)
        
        minbet_layout.addWidget(self.minbet_stack)
        minbet_group.setLayout(minbet_layout)
        layout.addRow(minbet_group)
        
        # Дополнительные поля
        settings_group = QGroupBox("Дополнительные настройки")
        settings_layout = QFormLayout()
        
        # IsLastNode
        self.is_last_node_check = QCheckBox()
        self.is_last_node_check.stateChanged.connect(self.update_node_data)
        settings_layout.addRow("IsLastNode:", self.is_last_node_check)
        
        # ResegmentFlag
        self.resegment_flag_check = QCheckBox()
        self.resegment_flag_check.setChecked(False)
        self.resegment_flag_check.stateChanged.connect(self.update_node_data)
        # settings_layout.addRow("ResegmentFlag:", self.resegment_flag_check)
        
        # MiniGame
        self.mini_game_edit = QLineEdit()
        self.mini_game_edit.setText("FlatReward")
        self.mini_game_edit.textChanged.connect(self.update_node_data)
        settings_layout.addRow("MiniGame:", self.mini_game_edit)
        
        # ButtonActionText
        self.button_action_text_edit = QLineEdit()
        self.button_action_text_edit.setText("GO WIN!")
        self.button_action_text_edit.textChanged.connect(self.update_node_data)
        settings_layout.addRow("ButtonActionText:", self.button_action_text_edit)
        
        # ButtonActionType
        self.button_action_type_combo = QLineEdit()
        self.button_action_type_combo.setText("")
        self.button_action_type_combo.textChanged.connect(self.update_node_data)
        settings_layout.addRow("ButtonActionType:", self.button_action_type_combo)
        
        # ButtonActionData
        self.button_action_data_edit = QLineEdit()
        self.button_action_data_edit.setText("")
        self.button_action_data_edit.textChanged.connect(self.update_node_data)
        settings_layout.addRow("ButtonActionData:", self.button_action_data_edit)
        
        # CustomTexts (многострочное поле)
        self.custom_texts_edit = QTextEdit()
        self.custom_texts_edit.setPlaceholderText("Каждый текст на новой строке")
        self.custom_texts_edit.textChanged.connect(self.update_node_data)
        settings_layout.addRow("CustomTexts:", self.custom_texts_edit)
        
        # PossibleItemCollect
        self.possible_item_collect_edit = QLineEdit()
        self.possible_item_collect_edit.textChanged.connect(self.update_node_data)
        settings_layout.addRow("PossibleItemCollect:", self.possible_item_collect_edit)
        
        # ContributionLevel
        self.contribution_combo = QComboBox()
        self.contribution_combo.addItems(["Stage", "Node"])
        self.contribution_combo.setCurrentText("Node")
        self.contribution_combo.currentTextChanged.connect(self.update_node_data)
        # settings_layout.addRow("ContributionLevel:", self.contribution_combo)
        
        # PrizeBoxIndex
        self.prize_box_index_spin = QSpinBox()
        self.prize_box_index_spin.setRange(0, 100)
        self.prize_box_index_spin.setValue(0)
        self.prize_box_index_spin.valueChanged.connect(self.update_node_data)
        settings_layout.addRow("PrizeBoxIndex:", self.prize_box_index_spin)
        
        # IsChoiceEvent
        self.is_choice_event_check = QCheckBox()
        self.is_choice_event_check.setChecked(False)
        self.is_choice_event_check.stateChanged.connect(self.update_node_data)
        settings_layout.addRow("IsChoiceEvent:", self.is_choice_event_check)
        
        # HideLoadingScreenForReward
        self.hide_loading_screen_check = QCheckBox()
        self.hide_loading_screen_check.setChecked(False)
        self.hide_loading_screen_check.stateChanged.connect(self.update_node_data)
        settings_layout.addRow("HideLoadingScreenForReward:", self.hide_loading_screen_check)
        
        settings_group.setLayout(settings_layout)
        layout.addRow(settings_group)
        
        self.tab_widget.addTab(self.node_tab, "Node")
    
    def create_goal_tab(self):
        """Создать вкладку редактирования цели"""
        self.goal_tab = QWidget()
        layout = QVBoxLayout(self.goal_tab)
        
        # Панель управления целями
        goal_control_panel = QFrame()
        goal_control_layout = QHBoxLayout(goal_control_panel)
        
        self.add_goal_btn = QPushButton("Добавить цель")
        self.add_goal_btn.clicked.connect(self.add_goal_dialog)
        goal_control_layout.addWidget(self.add_goal_btn)
        
        self.remove_goal_btn = QPushButton("Удалить цель")
        self.remove_goal_btn.clicked.connect(self.remove_goal)
        goal_control_layout.addWidget(self.remove_goal_btn)
        
        layout.addWidget(goal_control_panel)
        
        # Список целей
        self.goals_list = QListWidget()
        self.goals_list.itemClicked.connect(self.on_goal_selected)
        layout.addWidget(self.goals_list)
        
        # Панель редактирования цели
        goal_edit_panel = QFrame()
        self.goal_edit_layout = QFormLayout(goal_edit_panel)
        layout.addWidget(goal_edit_panel)
        
        self.tab_widget.addTab(self.goal_tab, "Цель")
    
    def create_reward_tab(self):
        """Создать вкладку редактирования награды"""
        self.reward_tab = QWidget()
        layout = QVBoxLayout(self.reward_tab)
        
        # Панель управления наградами
        reward_control_panel = QFrame()
        reward_control_layout = QHBoxLayout(reward_control_panel)
        
        self.add_reward_btn = QPushButton("Добавить награду")
        self.add_reward_btn.clicked.connect(self.add_reward_dialog)
        reward_control_layout.addWidget(self.add_reward_btn)
        
        self.remove_reward_btn = QPushButton("Удалить награду")
        self.remove_reward_btn.clicked.connect(self.remove_reward)
        reward_control_layout.addWidget(self.remove_reward_btn)
        
        layout.addWidget(reward_control_panel)
        
        # Список наград
        self.rewards_list = QListWidget()
        self.rewards_list.itemClicked.connect(self.on_reward_selected)
        layout.addWidget(self.rewards_list)
        
        # Панель редактирования награды
        reward_edit_panel = QFrame()
        self.reward_edit_layout = QFormLayout(reward_edit_panel)
        layout.addWidget(reward_edit_panel)
        
        self.tab_widget.addTab(self.reward_tab, "Награды")
    
    def update_current_event(self):
        """Обновить данные текущего события"""
        if self.current_event:
            event = self.current_event
            
            event["EventID"] = self.event_id_edit.text()
            event["MinLevel"] = self.min_level.value()
            event["AssetBundlePath"] = self.event_bundle_path.text()
            event["BlockerPrefabPath"] = self.event_blocker_path.text()
            event["NodeCompletionPrefabPath"] = self.event_node_path.text()
            event["EventCardPrefabPath"] = self.event_event_card_path.text()
            event["RoundelPrefabPath"] = self.event_roundel_path.text()
            event["ContentKey"] = self.event_content_key.text()
            event["NumberOfRepeats"] = self.repeats.value()
            event["IsRoundelHidden"] = self.hide_roundel.isChecked()
            event["ShowRoundelOnAllMachines"] = self.show_roundel_on_all_machines.isChecked()
            event["IsCurrencyEvent"] = self.is_currency_event_check.isChecked()
            event["StartingEventCurrency"] = self.starting_currency.value()
            event["EntryTypes"] = self.parse_entry_types(self.entry_types.text())
            event["TimeWarning"] = self.time_warning_edit.dateTime().toString("yyyy-MM-ddTHH:mm:ssZ")
            
            # Обновляем имя в списке событий
            self.events_list.item(self.current_event_index).setText(
                f"{event['EventID']} (Ур. {event['MinLevel']})"
            )
            
            self.update_event_tree()
    
    def load_segment_into_ui(self, segment_name):
        """Загрузить данные сегмента в UI"""
        if self.current_event and segment_name in self.current_event.get("Segments", {}):
            segment = self.current_event["Segments"][segment_name]
            info = segment.get("PossibleSegmentInfo", {})
            
            self.segment_name_edit.setText(segment_name)
            self.avg_wager_edit.setText(info.get("AverageWagerRange", ""))
            self.spinpad_edit.setText(info.get("SpinpadRange", ""))
            self.level_edit.setText(info.get("LevelRange", ""))
            self.vip_edit.setText(info.get("VIPRange", ""))
    
    def update_segment_data(self):
        """Обновить данные сегмента"""
        if not self.current_event or not self.current_segment:
            return
            
        event = self.current_event
        old_segment_name = self.current_segment
        new_segment_name = self.segment_name_edit.text().strip()
        
        if not new_segment_name:
            QMessageBox.warning(self, "Ошибка", "Название сегмента не может быть пустым")
            return
        
        # Проверяем существует ли сегмент с новым именем (если имя изменилось)
        if new_segment_name != old_segment_name and new_segment_name in event["Segments"]:
            QMessageBox.warning(self, "Ошибка", f"Сегмент с именем '{new_segment_name}' уже существует")
            return
        
        # Получаем или создаем сегмент
        if old_segment_name in event["Segments"]:
            segment = event["Segments"][old_segment_name]
            
            # Если имя изменилось, переименовываем сегмент
            if new_segment_name != old_segment_name:
                event["Segments"][new_segment_name] = segment
                del event["Segments"][old_segment_name]
                self.current_segment = new_segment_name
        else:
            # Создаем новый сегмент
            segment = {"PossibleSegmentInfo": {}, "Stages": []}
            event["Segments"][new_segment_name] = segment
        
        # Обновляем информацию о сегменте
        info = segment.setdefault("PossibleSegmentInfo", {})
        
        # Обновляем только непустые значения
        vip_range = self.vip_edit.text().strip()
        if vip_range:
            info["VIPRange"] = vip_range
        elif "VIPRange" in info:
            del info["VIPRange"]
        
        avg_wager = self.avg_wager_edit.text().strip()
        if avg_wager:
            info["AverageWagerRange"] = avg_wager
        elif "AverageWagerRange" in info:
            del info["AverageWagerRange"]
        
        spinpad = self.spinpad_edit.text().strip()
        if spinpad:
            info["SpinpadRange"] = spinpad
        elif "SpinpadRange" in info:
            del info["SpinpadRange"]
        
        level = self.level_edit.text().strip()
        if level:
            info["LevelRange"] = level
        elif "LevelRange" in info:
            del info["LevelRange"]
        
        # Обновляем дерево
        self.update_event_tree()
        
        self.statusBar().showMessage(f'Сегмент "{new_segment_name}" обновлен')
    
    def update_stage_data(self):
        """Обновить данные этапа"""
        if self.current_event and self.current_segment and self.current_stage is not None:
            event = self.current_event
            
            if self.current_segment in event["Segments"]:
                segment = event["Segments"][self.current_segment]
                
                # Находим и обновляем этап
                for stage in segment.get("Stages", []):
                    if stage["StageID"] == self.current_stage:
                        stage["StageID"] = self.stage_id_spin.value()
                        self.current_stage = stage["StageID"]
    
    def update_node_data(self):
        """Обновить данные узла"""
        if self.current_event and self.current_segment and self.current_stage is not None and self.current_node is not None:
            event = self.current_event
            
            if self.current_segment in event["Segments"]:
                segment = event["Segments"][self.current_segment]
                
                # Находим текущий этап
                current_stage = None
                for stage in segment.get("Stages", []):
                    if stage["StageID"] == self.current_stage:
                        current_stage = stage
                        break
                
                if current_stage:
                    # Находим и обновляем узел
                    for node_wrapper in current_stage.get("Nodes", []):
                        for node_type, node_data in node_wrapper.items():
                            if node_data.get("NodeID") == self.current_node:
                                # Обновляем данные узла
                                node_data["NodeID"] = self.node_id_spin.value()
                                
                                # Парсим NextNodeID из текстового поля (всегда список)
                                next_node_id_text = self.next_node_id_spin.text().strip()
                                next_node_list = []
                                if next_node_id_text:
                                    for token in next_node_id_text.split(','):
                                        token = token.strip()
                                        if not token:
                                            continue

                                        # Стараемся распарсить число
                                        try:
                                            val = float(token)
                                        except ValueError:
                                            continue

                                        # Если это целое (например 3.0) — приводим к int
                                        if val.is_integer():
                                            next_node_list.append(int(val))
                                        else:
                                            # Оставляем float только если игра реально это поддерживает
                                            next_node_list.append(val)

                                node_data["NextNodeID"] = next_node_list
                                
                                # Парсим список игр из текстового поля
                                games_text = self.games_edit.text().strip()
                                if games_text:
                                    # Разделяем по запятым, убираем пробелы и пустые строки
                                    game_list = [game.strip() for game in games_text.split(',') if game.strip()]
                                    node_data["GameList"] = game_list
                                else:
                                    node_data["GameList"] = ["AllGames"]
                                
                                # Обновляем MinBet
                                if self.minbet_type_combo.currentText() == "Фиксированная":
                                    node_data["MinBet"] = {
                                        "FixedMinBet": {
                                            "MinBet": self.minbet_fixed_spin.value()
                                        }
                                    }
                                else:
                                    node_data["MinBet"] = {
                                        "MinBetVariable": {
                                            "Variable": self.minbet_variable_spin.value(),
                                            "Min": self.minbet_min_spin.value(),
                                            "Max": self.minbet_max_spin.value()
                                        }
                                    }
                                
                                # Обновляем новые параметры
                                node_data["PrizeBoxIndex"] = self.prize_box_index_spin.value()
                                node_data["HideLoadingScreenForReward"] = self.hide_loading_screen_check.isChecked()
                                node_data["IsChoiceEvent"] = self.is_choice_event_check.isChecked();
                                
                                # Обновляем остальные поля
                                node_data["IsLastNode"] = self.is_last_node_check.isChecked()
                                node_data["ResegmentFlag"] = self.resegment_flag_check.isChecked()
                                node_data["MiniGame"] = self.mini_game_edit.text()
                                node_data["ButtonActionText"] = self.button_action_text_edit.text()
                                node_data["ButtonActionType"] = self.button_action_type_combo.text()
                                node_data["ButtonActionData"] = self.button_action_data_edit.text()
                                
                                # Парсим CustomTexts
                                custom_texts = self.custom_texts_edit.toPlainText().strip()
                                if custom_texts:
                                    node_data["CustomTexts"] = [line.strip() for line in custom_texts.split('\n') if line.strip()]
                                else:
                                    node_data["CustomTexts"] = []
                                
                                node_data["PossibleItemCollect"] = self.possible_item_collect_edit.text()
                                node_data["ContributionLevel"] = self.contribution_combo.currentText()
                                
                                # Сохраняем Goal и Rewards если они есть
                                if "Goal" not in node_data:
                                    node_data["Goal"] = {}
                                if "Rewards" not in node_data:
                                    node_data["Rewards"] = []
                                
                                self.current_node = node_data["NodeID"]
                                self.update_event_tree()
                                break
    
    def on_node_type_changed(self, node_type):
        """Обработчик изменения типа узла"""
        # Обновляем доступные поля в зависимости от типа узла
        if node_type == "DummyNode":
            self.next_node_id_spin.setEnabled(True)
            self.minbet_type_combo.setEnabled(False)
            self.minbet_stack.setEnabled(False)
            self.games_edit.setEnabled(False)
            self.prize_box_index_spin.setEnabled(False)
            self.hide_loading_screen_check.setEnabled(False)
            self.is_last_node_check.setEnabled(False)
            self.resegment_flag_check.setEnabled(True)
            self.mini_game_edit.setEnabled(True)
            self.button_action_text_edit.setEnabled(True)
            self.button_action_type_combo.setEnabled(True)
            self.button_action_data_edit.setEnabled(True)
            self.custom_texts_edit.setEnabled(True)
            self.possible_item_collect_edit.setEnabled(False)
            self.contribution_combo.setEnabled(True)
            self.is_choice_event_check.setEnabled(True)           
        elif node_type == "ProgressNode":        
            self.next_node_id_spin.setEnabled(True)
            self.minbet_type_combo.setEnabled(True)
            self.minbet_stack.setEnabled(True)
            self.games_edit.setEnabled(True)
            self.prize_box_index_spin.setEnabled(True)
            self.hide_loading_screen_check.setEnabled(True)
            self.is_last_node_check.setEnabled(True)
            self.resegment_flag_check.setEnabled(True)
            self.mini_game_edit.setEnabled(True)
            self.button_action_text_edit.setEnabled(True)
            self.button_action_type_combo.setEnabled(True)
            self.button_action_data_edit.setEnabled(True)
            self.custom_texts_edit.setEnabled(True)
            self.possible_item_collect_edit.setEnabled(True)
            self.contribution_combo.setEnabled(True)
            self.is_choice_event_check.setEnabled(False)
        elif node_type == "EntriesNode":        
            self.next_node_id_spin.setEnabled(False)
            self.minbet_type_combo.setEnabled(True)
            self.minbet_stack.setEnabled(True)
            self.games_edit.setEnabled(True)
            self.prize_box_index_spin.setEnabled(False)
            self.hide_loading_screen_check.setEnabled(False)
            self.is_last_node_check.setEnabled(False)
            self.resegment_flag_check.setEnabled(True)
            self.mini_game_edit.setEnabled(False)
            self.button_action_text_edit.setEnabled(True)
            self.button_action_type_combo.setEnabled(True)
            self.button_action_data_edit.setEnabled(True)
            self.custom_texts_edit.setEnabled(True)
            self.possible_item_collect_edit.setEnabled(True)
            self.contribution_combo.setEnabled(True)
            self.is_choice_event_check.setEnabled(False)
        else:        
            self.next_node_id_spin.setEnabled(True)
            self.minbet_type_combo.setEnabled(True)
            self.minbet_stack.setEnabled(True)
            self.games_edit.setEnabled(True)
            self.prize_box_index_spin.setEnabled(True)
            self.hide_loading_screen_check.setEnabled(True)
            self.is_last_node_check.setEnabled(True)
            self.resegment_flag_check.setEnabled(True)
            self.mini_game_edit.setEnabled(True)
            self.button_action_text_edit.setEnabled(True)
            self.button_action_type_combo.setEnabled(True)
            self.button_action_data_edit.setEnabled(True)
            self.custom_texts_edit.setEnabled(True)
            self.possible_item_collect_edit.setEnabled(True)
            self.contribution_combo.setEnabled(True)           
            self.is_choice_event_check.setEnabled(False)
            
        # Обновляем данные узла если есть текущий узел
        if self.current_node is not None:
            self.update_node_data()
    
    def on_minbet_type_changed(self, bet_type):
        """Обработчик изменения типа MinBet"""
        if bet_type == "Фиксированная":
            self.minbet_stack.setCurrentIndex(0)  # Показываем фиксированную ставку
        else:
            self.minbet_stack.setCurrentIndex(1)  # Показываем переменную ставку
        
        # Обновляем данные узла если есть текущий узел
        if self.current_node is not None:
            self.update_node_data()
    
    def on_goal_type_changed(self, goal_type):
        """Обработчик изменения типа цели"""
        # Очищаем поля
        self.clear_layout(self.goal_edit_layout)
        self.goal_widgets.clear()
        
        # Добавляем соответствующие поля
        if goal_type == "FixedGoal":
            target_spin = QDoubleSpinBox()
            target_spin.setRange(0, 100000000)
            target_spin.setValue(10000)
            self.goal_edit_layout.addRow("Цель:", target_spin)
            self.goal_widgets["Target"] = target_spin
            
        elif goal_type == "ConsecutiveWinsGoal":
            wins_spin = QSpinBox()
            wins_spin.setRange(1, 100)
            wins_spin.setValue(3)
            self.goal_edit_layout.addRow("Побед подряд:", wins_spin)
            self.goal_widgets["Wins"] = wins_spin
            
            multiplier_spin = QDoubleSpinBox()
            multiplier_spin.setRange(0.1, 100)
            multiplier_spin.setValue(2.5)
            self.goal_edit_layout.addRow("Множитель:", multiplier_spin)
            self.goal_widgets["Multiplier"] = multiplier_spin
            
            min_spin = QSpinBox()
            min_spin.setRange(1, 1000)
            min_spin.setValue(1)
            self.goal_edit_layout.addRow("Мин:", min_spin)
            self.goal_widgets["Min"] = min_spin
            
            max_spin = QSpinBox()
            max_spin.setRange(1, 10000)
            max_spin.setValue(5)
            self.goal_edit_layout.addRow("Макс:", max_spin)
            self.goal_widgets["Max"] = max_spin
        
        elif goal_type == "SpinpadGoal":
            spinpad_spin = QSpinBox()
            spinpad_spin.setRange(1, 1000)
            spinpad_spin.setValue(100)
            self.goal_edit_layout.addRow("Количество спинов:", spinpad_spin)
            self.goal_widgets["Spinpad"] = spinpad_spin
    
    def clear_layout(self, layout):
        """Очистить layout"""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    def create_new_file(self):
        """Создать новый файл с пустым списком событий"""
        reply = QMessageBox.question(
            self, 'Новый файл',
            'Вы уверены, что хотите создать новый файл? Несохраненные данные будут потеряны.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.events = []
            self.current_event_index = -1
            self.events_list.clear()
            self.tree_widget.clear()
            self.clear_ui()
            self.statusBar().showMessage('Создан новый файл')
    
    def create_new_event(self):
        """Создать новое событие (с сегментом VIP_1 и этапом StageID: 1 по умолчанию)"""
        event = {
            "EventID": "New_Event_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
            "MinLevel": 70,
            "TimeWarning": QDateTime.currentDateTime().addDays(14).toString("yyyy-MM-ddTHH:mm:ssZ"),
            "AssetBundlePath": "_events/AncientDragonChallenge",
            "BlockerPrefabPath": "Dialog/AncientDragonChallenge_Dialog",
            "NodeCompletionPrefabPath": "Dialog/AncientDragonChallenge_Dialog",
            "RoundelPrefabPath": "Roundel/AncientDragonChallenge_Roundel",
            "EventCardPrefabPath": "EventCard/AncientDragonChallenge_EventCard",
            "ContentKey": "AncientDragonChallenge",
            "NumberOfRepeats": -1,           
            "IsRoundelHidden": False,
            "ShowRoundelOnAllMachines": True,
            "IsCurrencyEvent": False,
            "StartingEventCurrency": 0,
            "Segments": {},  # Создадим сегмент ниже
            "EntryTypes": []
        }
    
        # Создаем сегмент VIP_1 по умолчанию
        segment_name = "VIP_1"
        segment_info = {"VIPRange": "0-10"}
    
        # Создаем этап StageID: 1 по умолчанию
        stage_1 = {
            "StageID": 1,
            "Nodes": []
        }
    
        segment = {
            "PossibleSegmentInfo": segment_info,
            "Stages": [stage_1]  # Добавляем этап 1 автоматически
        }
    
        # Добавляем сегмент в событие
        event["Segments"][segment_name] = segment
    
        self.add_event_to_list(event)
    
        # Устанавливаем текущий сегмент и этап
        self.current_segment = segment_name
        self.current_stage = 1
    
        self.statusBar().showMessage(f'Создано новое событие с сегментом {segment_name} и этапом StageID: 1')
    
    def add_new_event(self):
        """Добавить новое событие через кнопку"""
        self.create_new_event()
    
    def add_event_to_list(self, event):
        """Добавить событие в список"""
        self.normalize_event_structure(event)

        self.events.append(event)
        self.current_event_index = len(self.events) - 1
        
        # Добавляем в список
        item_text = f"{event['EventID']} (Ур. {event['MinLevel']})"
        self.events_list.addItem(item_text)
        self.events_list.setCurrentRow(self.current_event_index)
        
        # Загружаем данные события в UI
        self.load_event_into_ui(event)
        
        self.update_event_tree()
        self.statusBar().showMessage(f'Добавлено событие: {event["EventID"]}')
    
    def remove_current_event(self):
        """Удалить текущее событие"""
        if self.current_event:
            event_id = self.current_event["EventID"]
            reply = QMessageBox.question(
                self, 'Удаление события',
                f'Вы уверены, что хотите удалить событие "{event_id}"?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Удаляем событие
                del self.events[self.current_event_index]
                self.events_list.takeItem(self.current_event_index)
                
                # Выбираем другое событие если есть
                if self.events:
                    self.current_event_index = min(self.current_event_index, len(self.events) - 1)
                    self.events_list.setCurrentRow(self.current_event_index)
                    self.load_event_into_ui(self.events[self.current_event_index])
                else:
                    self.current_event_index = -1
                    self.clear_ui()
                
                self.statusBar().showMessage(f'Событие удалено')
    
    def duplicate_current_event(self):
        """Дублировать текущее событие"""
        if self.current_event:
            # Создаем глубокую копию
            duplicate = copy.deepcopy(self.current_event)
            
            # Меняем ID
            duplicate["EventID"] = f"{self.current_event['EventID']}_Copy_{datetime.now().strftime('%H%M%S')}"
            
            self.add_event_to_list(duplicate)
            self.statusBar().showMessage(f'Событие продублировано')
    
    def on_event_selected(self, item):
        """Обработчик выбора события из списка"""
        row = self.events_list.row(item)
        if 0 <= row < len(self.events):
            self.current_event_index = row
            self.load_event_into_ui(self.events[row])
    
    def load_event_into_ui(self, event):
        """Загрузить данные события в UI"""
        self.event_id_edit.setText(event.get("EventID", ""))
        self.min_level.setValue(event.get("MinLevel", 70))
        self.event_bundle_path.setText(event.get("AssetBundlePath", ""))
        self.event_blocker_path.setText(event.get("BlockerPrefabPath", ""))
        self.event_node_path.setText(event.get("NodeCompletionPrefabPath", ""))
        self.event_event_card_path.setText(event.get("EventCardPrefabPath", ""))
        self.event_roundel_path.setText(event.get("RoundelPrefabPath", ""))
        self.event_content_key.setText(event.get("ContentKey", ""))
        self.repeats.setValue(event.get("NumberOfRepeats", -1))
        self.hide_roundel.setChecked(event.get("IsRoundelHidden", False))
        self.show_roundel_on_all_machines.setChecked(event.get("ShowRoundelOnAllMachines", True))
        self.is_currency_event_check.setChecked(event.get("IsCurrencyEvent", False))
        self.starting_currency.setValue(event.get("StartingEventCurrency", 0))
        self.entry_types.setText(", ".join(event.get("EntryTypes", [])))
        
        # Устанавливаем время предупреждения если есть
        if "TimeWarning" in event:
            try:
                dt = QDateTime.fromString(event["TimeWarning"], "yyyy-MM-ddTHH:mm:ssZ")
                self.time_warning_edit.setDateTime(dt)
            except:
                self.time_warning_edit.setDateTime(QDateTime.currentDateTime().addDays(14))
        
        # Выбираем сегмент VIP_1 если он существует, иначе первый сегмент
        target_segment = None
        target_stage = None
    
        # Пытаемся найти VIP_1
        if "VIP_1" in event.get("Segments", {}):
            target_segment = "VIP_1"
        elif event.get("Segments", {}):
            target_segment = list(event["Segments"].keys())[0]
    
        if target_segment:
            self.current_segment = target_segment
        
            # Загружаем данные сегмента
            self.load_segment_into_ui(target_segment)
        
            # Устанавливаем StageID: 1 как текущий этап
            if target_segment in event["Segments"]:
                segment = event["Segments"][target_segment]
                if segment.get("Stages"):
                    # Ищем StageID: 1
                    for stage in segment["Stages"]:
                        if stage.get("StageID") == 1:
                            target_stage = 1
                            break
                    # Если StageID: 1 не найден, берем первый этап
                    if not target_stage and segment["Stages"]:
                        target_stage = segment["Stages"][0]["StageID"]
                
                    self.current_stage = target_stage
                    self.stage_id_spin.setValue(target_stage if target_stage else 1)
        else:
            self.current_segment = None
            self.current_stage = None
    
        # Сбрасываем текущий узел
        self.current_node = None
    
        self.update_event_tree()
    
    def clear_ui(self):
        """Очистить UI"""
        self.event_id_edit.clear()
        self.min_level.setValue(0)
        self.event_bundle_path.clear()
        self.event_blocker_path.clear()
        self.event_node_path.clear()
        self.event_event_card_path.clear()
        self.event_roundel_path.clear()
        self.event_content_key.clear()
        self.repeats.setValue(-1)
        self.hide_roundel.setChecked(False)
        self.show_roundel_on_all_machines.setChecked(True)
        self.is_currency_event_check.setChecked(False)
        self.starting_currency.setValue(0)
        self.entry_types.clear()
        self.time_warning_edit.setDateTime(QDateTime.currentDateTime().addDays(14))
        
        # Очищаем остальные вкладки
        self.segment_name_edit.clear()
        self.avg_wager_edit.clear()
        self.spinpad_edit.clear()
        self.level_edit.clear()
        self.vip_edit.clear()
        
        self.stage_id_spin.setValue(1)
        
        self.node_id_spin.setValue(1)
        self.next_node_id_spin.setText(str(1))
        self.games_edit.clear()
        
        # Очищаем MinBet поля
        self.minbet_type_combo.setCurrentText("Фиксированная")
        self.on_minbet_type_changed("Фиксированная")
        self.minbet_fixed_spin.setValue(250000)
        self.minbet_variable_spin.setValue(0.8)
        self.minbet_min_spin.setValue(25000)
        self.minbet_max_spin.setValue(5000000)
        
        # Очищаем новые поля
        self.prize_box_index_spin.setValue(0)
        self.hide_loading_screen_check.setChecked(False)
        self.is_choice_event_check.setChecked(False)
        self.is_last_node_check.setChecked(False)
        self.resegment_flag_check.setChecked(False)
        self.mini_game_edit.setText("FlatReward")
        self.button_action_text_edit.setText("GO WIN!")
        self.button_action_type_combo.setText("")
        self.button_action_data_edit.setText("")
        self.custom_texts_edit.clear()
        self.possible_item_collect_edit.clear()
        self.contribution_combo.setCurrentText("Node")
        
        self.goals_list.clear()
        self.rewards_list.clear()
        self.clear_layout(self.goal_edit_layout)
        self.clear_layout(self.reward_edit_layout)
        
        self.tree_widget.clear()
    
    def add_segment(self):
        """Добавить новый сегмент с автоматическим именем и этапом StageID: 1"""
        if not self.current_event:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте событие")
            return
        
        # Генерируем уникальное имя для сегмента
        segment_counter = 1
        while True:
            segment_name = f"VIP_{segment_counter}"
            if segment_name not in self.current_event["Segments"]:
                break
            segment_counter += 1
        
        # Создаем новый сегмент с базовыми параметрами
        segment_info = {"VIPRange": "0-10"}
        
        # Создаем этап StageID: 1 автоматически
        stage_1 = {
            "StageID": 1,
            "Nodes": []
        }
        
        segment = {
            "PossibleSegmentInfo": segment_info,
            "Stages": [stage_1]  # Добавляем этап 1 автоматически
        }
        
        # Добавляем сегмент в событие
        self.current_event["Segments"][segment_name] = segment
        self.current_segment = segment_name
        self.current_stage = 1  # Устанавливаем текущий этап как 1
        
        # Загружаем данные сегмента в форму
        self.load_segment_into_ui(segment_name)
        
        # Устанавливаем ID этапа в спинбокс
        self.stage_id_spin.setValue(1)
        
        # Переключаемся на вкладку сегмента
        self.tab_widget.setCurrentWidget(self.segment_tab)
        
        self.update_event_tree()
        self.statusBar().showMessage(f'Добавлен сегмент: {segment_name} с этапом StageID: 1')
    
    def remove_current_segment(self):
        """Удалить текущий сегмент"""
        if not self.current_event or not self.current_segment:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите сегмент для удаления")
            return
        
        segment_name = self.current_segment
        
        reply = QMessageBox.question(
            self, 'Удаление сегмента',
            f'Вы уверены, что хотите удалить сегмент "{segment_name}"?\nВсе этапы и узлы в этом сегменте будут удалены.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Удаляем сегмент
            if segment_name in self.current_event["Segments"]:
                del self.current_event["Segments"][segment_name]
            
            # Выбираем другой сегмент если есть
            self.current_segment = None
            self.current_stage = None
            if self.current_event["Segments"]:
                first_segment = list(self.current_event["Segments"].keys())[0]
                self.current_segment = first_segment
                
                # Устанавливаем первый этап как текущий
                segment = self.current_event["Segments"][first_segment]
                if segment.get("Stages"):
                    self.current_stage = segment["Stages"][0]["StageID"]
                    self.stage_id_spin.setValue(self.current_stage)
            
            if self.current_segment:
                self.load_segment_into_ui(self.current_segment)
            else:
                self.clear_segment_ui()
                self.stage_id_spin.setValue(1)
            
            self.update_event_tree()
            
            self.statusBar().showMessage(f'Сегмент "{segment_name}" удален')
    
    def duplicate_current_segment(self):
        """Дублировать текущий сегмент"""
        if not self.current_event or not self.current_segment:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите сегмент для дублирования")
            return
        
        old_segment_name = self.current_segment
        
        # Генерируем уникальное имя для копии
        segment_counter = 1
        while True:
            new_segment_name = f"{old_segment_name}_Copy_{segment_counter}"
            if new_segment_name not in self.current_event["Segments"]:
                break
            segment_counter += 1
        
        # Создаем глубокую копию сегмента
        old_segment = self.current_event["Segments"][old_segment_name]
        new_segment = copy.deepcopy(old_segment)
        
        # Добавляем новый сегмент
        self.current_event["Segments"][new_segment_name] = new_segment
        self.current_segment = new_segment_name
        
        # Устанавливаем первый этап как текущий
        if new_segment.get("Stages"):
            self.current_stage = new_segment["Stages"][0]["StageID"]
            self.stage_id_spin.setValue(self.current_stage)
        
        # Загружаем данные сегмента в форму
        self.load_segment_into_ui(new_segment_name)
        
        self.update_event_tree()
        self.statusBar().showMessage(f'Сегмент "{old_segment_name}" продублирован как "{new_segment_name}"')
    
    def clear_segment_ui(self):
        """Очистить UI сегмента"""
        self.segment_name_edit.clear()
        self.avg_wager_edit.clear()
        self.spinpad_edit.clear()
        self.level_edit.clear()
        self.vip_edit.clear()
    
    def add_stage(self):
        """Добавить новый этап"""
        if not self.current_event or not self.current_segment:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите или создайте сегмент")
            return
        
        # Находим максимальный ID этапа в текущем сегменте
        max_stage_id = 0
        segment = self.current_event["Segments"][self.current_segment]
        for stage in segment.get("Stages", []):
            if stage["StageID"] > max_stage_id:
                max_stage_id = stage["StageID"]
        
        # Новый этап будет иметь ID на 1 больше максимального
        stage_id = max_stage_id + 1
        if stage_id < 1:
            stage_id = 1
            
        stage = {
            "StageID": stage_id,
            "Nodes": []
        }
        
        # Добавляем этап в текущий сегмент
        segment["Stages"].append(stage)
        self.current_stage = stage_id
        
        # Обновляем спинбокс ID этапа
        self.stage_id_spin.setValue(stage_id)
        
        self.update_event_tree()
        self.statusBar().showMessage(f'Добавлен этап: {stage_id}')
    
    def add_node_dialog(self):
        """Диалог добавления нового узла"""
        if not self.current_event or not self.current_segment or self.current_stage is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите или создайте этап")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить узел")
        layout = QVBoxLayout(dialog)
        
        node_type_combo = QComboBox()
        node_type_combo.addItems(["ProgressNode", "EntriesNode", "EntriesProgressNode", "DummyNode"])
        layout.addWidget(QLabel("Тип узла:"))
        layout.addWidget(node_type_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            node_type = node_type_combo.currentText()
            self.add_node(node_type)
    
    def add_node(self, node_type):
        """Добавить узел"""
        if not self.current_event or not self.current_segment or self.current_stage is None:
            return
        
        # Находим максимальный ID узла в текущем этапе
        max_node_id = 0
        segment = self.current_event["Segments"][self.current_segment]
        for stage in segment["Stages"]:
            if stage["StageID"] == self.current_stage:
                for node_wrapper in stage.get("Nodes", []):
                    for node_type_name, node_data in node_wrapper.items():
                        if node_data.get("NodeID", 0) > max_node_id:
                            max_node_id = node_data.get("NodeID", 0)
                break
        
        # Новый узел будет иметь ID на 1 больше максимального
        node_id = max_node_id + 1
        if node_id < 1:
            node_id = 1
            
        # Обновляем спинбокс ID узла
        self.node_id_spin.setValue(node_id)

        is_last = self.is_last_node_check.isChecked()
        default_next = [] if is_last else [node_id + 1]
        self.next_node_id_spin.setText("" if is_last else str(node_id + 1))
        
        # Парсим список игр из текстового поля
        games_text = self.games_edit.text().strip()
        if games_text:
            game_list = [game.strip() for game in games_text.split(',') if game.strip()]
        else:
            game_list = ["AllGames"]  # Значение по умолчанию
        
        # Парсим CustomTexts
        custom_texts = self.custom_texts_edit.toPlainText().strip()
        if custom_texts:
            custom_texts_list = [line.strip() for line in custom_texts.split('\n') if line.strip()]
        else:
            custom_texts_list = ["COLLECT", "##", "GREENDRAGON SYMBOLS", "70,000,000"]  # Значения по умолчанию
        
        # Создаем базовую структуру узла
        node = {
            "NodeID": node_id,
            "NextNodeID": default_next,
            "GameList": game_list,
            "MinBet": {},
            "Goal": {},
            "Rewards": [],           
            "IsLastNode": self.is_last_node_check.isChecked(),
            "IsChoiceEvent": self.is_choice_event_check.isChecked(),
            "ResegmentFlag": self.resegment_flag_check.isChecked(),
            "MiniGame": self.mini_game_edit.text() or "FlatReward",
            "ButtonActionText": self.button_action_text_edit.text() or "GO WIN!",
            "ButtonActionType": self.button_action_type_combo.text() or "",
            "ButtonActionData": self.button_action_data_edit.text() or "",
            "CustomTexts": custom_texts_list,
            "PossibleItemCollect": self.possible_item_collect_edit.text(),
            "ContributionLevel": self.contribution_combo.currentText(),
            "PrizeBoxIndex": self.prize_box_index_spin.value(),
            "HideLoadingScreenForReward": self.hide_loading_screen_check.isChecked()
        }
        
        # Добавляем MinBet
        if self.minbet_type_combo.currentText() == "Фиксированная":
            node["MinBet"] = {
                "FixedMinBet": {
                    "MinBet": self.minbet_fixed_spin.value()
                }
            }
        else:
            node["MinBet"] = {
                "MinBetVariable": {
                    "Variable": self.minbet_variable_spin.value(),
                    "Min": self.minbet_min_spin.value(),
                    "Max": self.minbet_max_spin.value()
                }
            }
        
        # Добавляем в текущий этап
        for stage in segment["Stages"]:
            if stage["StageID"] == self.current_stage:
                # Создаем узел нужного типа
                if node_type == "ProgressNode":
                    stage["Nodes"].append({"ProgressNode": node})
                elif node_type == "EntriesNode":
                    stage["Nodes"].append({"EntriesNode": node})
                elif node_type == "EntriesProgressNode":
                    stage["Nodes"].append({"EntriesProgressNode": node})
                elif node_type == "DummyNode":
                    stage["Nodes"].append({"DummyNode": node})
                
                self.current_node = node_id
                break
        
        self.update_event_tree()
        self.statusBar().showMessage(f'Добавлен узел {node_type}: {node_id}')
    
    def on_tree_item_clicked(self, item, column):
        """Обработчик клика по элементу дерева"""
        try:
            item_type = item.data(0, Qt.UserRole)
            item_id = item.data(0, Qt.UserRole + 1)

            if item_type == "event":
                self.tab_widget.setCurrentWidget(self.event_tab)
                return

            if item_type == "segment":
                self.current_segment = item_id
                self.tab_widget.setCurrentWidget(self.segment_tab)

                # Загружаем данные сегмента
                if self.current_event:
                    self.load_segment_into_ui(item_id)
                return

            if item_type == "stage":
                self.current_stage = item_id
                self.tab_widget.setCurrentWidget(self.stage_tab)
                self.stage_id_spin.setValue(item_id)
                return

            if item_type == "node":
                self.current_node = item_id
                self.tab_widget.setCurrentWidget(self.node_tab)
                self.node_id_spin.setValue(item_id)

                # Загружаем данные узла
                if not (self.current_event and self.current_segment and self.current_stage is not None):
                    return

                segment = self.current_event["Segments"].get(self.current_segment)
                if not segment:
                    return

                for stage in segment.get("Stages", []):
                    if stage.get("StageID") != self.current_stage:
                        continue

                    for node_wrapper in stage.get("Nodes", []):
                        for node_type, node_data in node_wrapper.items():
                            if node_data.get("NodeID") != item_id:
                                continue

                            # NextNodeID (нормализуем к списку для UI и экспорта)
                            next_node_id = node_data.get("NextNodeID")
                            if next_node_id is None:
                                next_node_list = []
                            elif isinstance(next_node_id, list):
                                next_node_list = next_node_id
                            else:
                                next_node_list = [next_node_id]

                            # Сохраняем нормализованное значение обратно (важно для старых конфигов)
                            node_data["NextNodeID"] = next_node_list
                            self.next_node_id_spin.setText(", ".join(str(x) for x in next_node_list) if next_node_list else "")

                            # GameList
                            game_list = node_data.get("GameList", [])
                            self.games_edit.setText(", ".join(game_list) if game_list else "")

                            # MinBet
                            minbet = node_data.get("MinBet", {})
                            if "FixedMinBet" in minbet:
                                self.minbet_type_combo.setCurrentText("Фиксированная")
                                self.on_minbet_type_changed("Фиксированная")
                                self.minbet_fixed_spin.setValue(minbet["FixedMinBet"].get("MinBet", 250000))
                            elif "MinBetVariable" in minbet:
                                self.minbet_type_combo.setCurrentText("Переменная")
                                self.on_minbet_type_changed("Переменная")
                                self.minbet_variable_spin.setValue(minbet["MinBetVariable"].get("Variable", 0.8))
                                self.minbet_min_spin.setValue(minbet["MinBetVariable"].get("Min", 25000))
                                self.minbet_max_spin.setValue(minbet["MinBetVariable"].get("Max", 5000000))
                            else:
                                # По умолчанию
                                self.minbet_type_combo.setCurrentText("Фиксированная")
                                self.on_minbet_type_changed("Фиксированная")

                            # Тип узла
                            if node_type in ["ProgressNode", "EntriesNode", "EntriesProgressNode", "DummyNode"]:
                                self.node_type_combo.setCurrentText(node_type)
                                self.on_node_type_changed(node_type)

                            # Параметры
                            self.prize_box_index_spin.setValue(node_data.get("PrizeBoxIndex", 0))
                            self.hide_loading_screen_check.setChecked(node_data.get("HideLoadingScreenForReward", False))
                            self.is_choice_event_check.setChecked(node_data.get("IsChoiceEvent", False))

                            self.is_last_node_check.setChecked(node_data.get("IsLastNode", False))
                            self.resegment_flag_check.setChecked(node_data.get("ResegmentFlag", False))
                            self.mini_game_edit.setText(node_data.get("MiniGame", "FlatReward"))
                            self.button_action_text_edit.setText(node_data.get("ButtonActionText", "GO WIN!"))

                            self.button_action_type_combo.setText(node_data.get("ButtonActionType", ""))
                            self.button_action_data_edit.setText(node_data.get("ButtonActionData", ""))

                            custom_texts = node_data.get("CustomTexts", [])
                            self.custom_texts_edit.setText("\n".join(custom_texts))

                            self.possible_item_collect_edit.setText(node_data.get("PossibleItemCollect", ""))

                            contribution = node_data.get("ContributionLevel", "Node")
                            if contribution in ["Stage", "Node"]:
                                self.contribution_combo.setCurrentText(contribution)

                            # Цели
                            self.goals_list.clear()
                            goals = node_data.get("Goal", {})
                            if goals and isinstance(goals, dict):
                                for goal_type in goals.keys():
                                    self.goals_list.addItem(goal_type)

                            # Награды
                            self.rewards_list.clear()
                            rewards = node_data.get("Rewards", [])
                            for reward in rewards:
                                if "FixedReward" in reward:
                                    fixed = reward["FixedReward"]
                                    self.rewards_list.addItem(
                                        f"{fixed.get('Currency', 'Unknown')}: {fixed.get('Amount', 0)}"
                                    )

                            return

        except Exception as e:
            print(f"Ошибка при обработке клика: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка при загрузке данных: {str(e)}")

    def update_event_tree(self):
        """Обновить дерево структуры"""
        self.tree_widget.clear()
        
        if not self.current_event:
            return
        
        event = self.current_event
        
        # Корневой элемент - событие
        event_item = QTreeWidgetItem([event["EventID"]])
        event_item.setData(0, Qt.UserRole, "event")
        self.tree_widget.addTopLevelItem(event_item)
        
        # Сегменты
        for segment_name, segment in event.get("Segments", {}).items():
            segment_item = QTreeWidgetItem([segment_name])
            segment_item.setData(0, Qt.UserRole, "segment")
            segment_item.setData(0, Qt.UserRole + 1, segment_name)
            event_item.addChild(segment_item)
            
            # Этапы
            for stage in segment.get("Stages", []):
                stage_item = QTreeWidgetItem([f"StageID {stage['StageID']}"])
                stage_item.setData(0, Qt.UserRole, "stage")
                stage_item.setData(0, Qt.UserRole + 1, stage["StageID"])
                segment_item.addChild(stage_item)
                
                # Узлы
                for node_wrapper in stage.get("Nodes", []):
                    for node_type, node_data in node_wrapper.items():
                        node_item = QTreeWidgetItem([f"{node_type} #{node_data.get('NodeID', '?')}"])
                        node_item.setData(0, Qt.UserRole, "node")
                        node_item.setData(0, Qt.UserRole + 1, node_data.get('NodeID', 0))
                        stage_item.addChild(node_item)
        
        # Раскрываем все элементы
        self.tree_widget.expandAll()
    
    def save_event_file(self):
        """Сохранить все события в файл"""
        if not self.events:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить события", "", "JSON Files (*.json)"
        )
        
        if filename:
            # Собираем полную структуру для всех событий
            event_data_list = []
            
            for event in self.events:
                self.normalize_event_structure(event)
                # Создаем структуру события в формате PossibleNodeEventData
                event_data = {
                    "PossibleNodeEventData": {
                        "EventID": event.get("EventID", ""),
                        "MinLevel": event.get("MinLevel", 70),
                        "TimeWarning": event.get("TimeWarning", QDateTime.currentDateTime().addDays(14).toString("yyyy-MM-ddTHH:mm:ssZ")),
                        "AssetBundlePath": event.get("AssetBundlePath", ""),
                        "BlockerPrefabPath": event.get("BlockerPrefabPath", ""),
                        "NodeCompletionPrefabPath": event.get("NodeCompletionPrefabPath", ""),
                        "EventCardPrefabPath": event.get("EventCardPrefabPath", ""),
                        "RoundelPrefabPath": event.get("RoundelPrefabPath", ""),
                        "ContentKey": event.get("ContentKey", ""),
                        "NumberOfRepeats": event.get("NumberOfRepeats", -1),
                        "IsRoundelHidden": event.get("IsRoundelHidden", False),
                        "ShowRoundelOnAllMachines": event.get("ShowRoundelOnAllMachines", True),
                        "IsCurrencyEvent": event.get("IsCurrencyEvent", False),
                        "StartingEventCurrency": event.get("StartingEventCurrency", 0),
                        "EntryTypes": event.get("EntryTypes", []),
                        "Segments": event.get("Segments", {})
                    }
                }
                event_data_list.append(event_data)
            
            full_data = {
                "Events": event_data_list,
                "IsFallbackConfig": False
            }
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(full_data, f, indent=2, ensure_ascii=False)
                self.statusBar().showMessage(f'Сохранено {len(self.events)} событий в {filename}')
                QMessageBox.information(self, "Успех", f"Файл успешно сохранен! Событий: {len(self.events)}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def parse_entry_types(self, text):
        """Парсинг строки EntryTypes"""
        if not text:
            return []
        # Преобразуем строку в список
        return [item.strip() for item in text.split(',') if item.strip()]


    def normalize_event_structure(self, event: dict) -> None:
        """Нормализовать структуру события перед экспортом/сохранением.

        Сейчас гарантируем, что NextNodeID всегда список (list), даже если в старом JSON было число.
        """
        if not isinstance(event, dict):
            return

        segments = event.get("Segments")
        if not isinstance(segments, dict):
            return

        for _seg_name, segment in segments.items():
            if not isinstance(segment, dict):
                continue
            stages = segment.get("Stages", [])
            if not isinstance(stages, list):
                continue

            for stage in stages:
                if not isinstance(stage, dict):
                    continue
                nodes = stage.get("Nodes", [])
                if not isinstance(nodes, list):
                    continue

                for node_wrapper in nodes:
                    if not isinstance(node_wrapper, dict):
                        continue
                    for _node_type, node_data in node_wrapper.items():
                        if not isinstance(node_data, dict):
                            continue

                        nn = node_data.get("NextNodeID")
                        if nn is None:
                            node_data["NextNodeID"] = []
                        elif isinstance(nn, list):
                            # ок
                            pass
                        else:
                            node_data["NextNodeID"] = [nn]
    
    def open_event_file(self):
        """Открыть события из файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть события", "", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Очищаем текущие данные
                self.events = []
                self.events_list.clear()
                
                # Загружаем события из файла
                if data.get("Events"):
                    for event_data in data["Events"]:
                        if "PossibleNodeEventData" in event_data:
                            event_data = event_data["PossibleNodeEventData"]
                        
                        # Создаем структуру события
                        event = {
                            "EventID": event_data.get("EventID", ""),
                            "MinLevel": event_data.get("MinLevel", 70),
                            "AssetBundlePath": event_data.get("AssetBundlePath", ""),
                            "BlockerPrefabPath": event_data.get("BlockerPrefabPath", ""),
                            "NodeCompletionPrefabPath": event_data.get("NodeCompletionPrefabPath", ""),
                            "EventCardPrefabPath": event_data.get("EventCardPrefabPath", ""),
                            "RoundelPrefabPath": event_data.get("RoundelPrefabPath", ""),
                            "ContentKey": event_data.get("ContentKey", ""),
                            "NumberOfRepeats": event_data.get("NumberOfRepeats", -1),
                            "IsRoundelHidden": event_data.get("IsRoundelHidden", False),
                            "ShowRoundelOnAllMachines": event_data.get("ShowRoundelOnAllMachines", True),
                            "IsCurrencyEvent": event_data.get("IsCurrencyEvent", False),
                            "StartingEventCurrency": event_data.get("StartingEventCurrency", 0),
                            "EntryTypes": event_data.get("EntryTypes", []),
                            "TimeWarning": event_data.get("TimeWarning", QDateTime.currentDateTime().addDays(14).toString("yyyy-MM-ddTHH:mm:ssZ")),
                            "Segments": event_data.get("Segments", {})
                        }
                        
                        self.events.append(event)
                        
                        # Добавляем в список
                        item_text = f"{event['EventID']} (Ур. {event['MinLevel']})"
                        self.events_list.addItem(item_text)
                
                # Выбираем первое событие если есть
                if self.events:
                    self.current_event_index = 0
                    self.events_list.setCurrentRow(0)
                    self.load_event_into_ui(self.events[0])
                
                self.statusBar().showMessage(f'Загружено {len(self.events)} событий из {filename}')
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def validate_all_events(self):
        """Проверить валидность всех событий"""
        if not self.events:
            QMessageBox.warning(self, "Ошибка", "Нет событий для проверки")
            return
        
        all_errors = []
        valid_events = 0
        
        for i, event in enumerate(self.events):
            errors = []
            
            # Проверка основных полей
            if not event.get("EventID"):
                errors.append("ID события не заполнен")
            
            if not event.get("Segments"):
                errors.append("Нет ни одного сегмента")
            
            # Проверка сегментов
            for seg_name, segment in event.get("Segments", {}).items():
                if not segment.get("Stages"):
                    errors.append(f"Сегмент '{seg_name}' не содержит этапов")
                
                for stage in segment.get("Stages", []):
                    if not stage.get("Nodes"):
                        errors.append(f"Этап {stage.get('StageID')} в сегменте '{seg_name}' не содержит узлов")
            
            if errors:
                error_msg = f"Событие {event['EventID']}:\n" + "\n".join(f"  • {error}" for error in errors)
                all_errors.append(error_msg)
            else:
                valid_events += 1
        
        if all_errors:
            error_msg = "Найдены ошибки:\n\n" + "\n\n".join(all_errors)
            QMessageBox.warning(self, "Проверка не пройдена", 
                              f"Проверено {len(self.events)} событий\n\n{error_msg}")
        else:
            QMessageBox.information(self, "Проверка пройдена", 
                                  f"Все {len(self.events)} событий корректны!")
    
    def export_json(self):
        """Экспортировать JSON в текстовое поле"""
        if not self.events:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта")
            return
        
        # Создаем диалог с предпросмотром JSON
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Предпросмотр JSON ({len(self.events)} событий)")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Текстовое поле с JSON
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Courier", 10))
        
        # Формируем JSON для всех событий
        event_data_list = []
        
        for event in self.events:
            self.normalize_event_structure(event)
            event_data = {
                "PossibleNodeEventData": {
                    "EventID": event.get("EventID", ""),
                    "MinLevel": event.get("MinLevel", 70),
                    "TimeWarning": event.get("TimeWarning", QDateTime.currentDateTime().addDays(14).toString("yyyy-MM-ddTHH:mm:ssZ")),
                    "AssetBundlePath": event.get("AssetBundlePath", ""),
                    "BlockerPrefabPath": event.get("BlockerPrefabPath", ""),
                    "NodeCompletionPrefabPath": event.get("NodeCompletionPrefabPath", ""),
                    "EventCardPrefabPath": event.get("EventCardPrefabPath", ""),
                    "RoundelPrefabPath": event.get("RoundelPrefabPath", ""),
                    "ContentKey": event.get("ContentKey", ""),
                    "NumberOfRepeats": event.get("NumberOfRepeats", -1),
                    "IsRoundelHidden": event.get("IsRoundelHidden", False),
                    "ShowRoundelOnAllMachines": event.get("ShowRoundelOnAllMachines", True),
                    "IsCurrencyEvent": event.get("IsCurrencyEvent", False),
                    "StartingEventCurrency": event.get("StartingEventCurrency", 0),
                    "EntryTypes": event.get("EntryTypes", []),
                    "Segments": event.get("Segments", {})
                }
            }
            event_data_list.append(event_data)
        
        full_data = {
            "Events": event_data_list,
            "IsFallbackConfig": False
        }
        
        text_edit.setText(json.dumps(full_data, indent=2, ensure_ascii=False))
        layout.addWidget(text_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.exec_()
    
    def add_goal_dialog(self):
        """Диалог добавления цели"""
        if not self.current_event or not self.current_segment or self.current_stage is None or self.current_node is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите или создайте узел")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить цель")
        layout = QVBoxLayout(dialog)
        
        goal_type_combo = QComboBox()
        goal_type_combo.addItems(["FixedGoal", "ConsecutiveWinsGoal", "SpinpadGoal"])
        layout.addWidget(QLabel("Тип цели:"))
        layout.addWidget(goal_type_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            goal_type = goal_type_combo.currentText()
            self.add_goal(goal_type)
    
    def add_goal(self, goal_type):
        """Добавить цель"""
        if not self.current_event or not self.current_segment or self.current_stage is None or self.current_node is None:
            return
        
        # Находим узел
        segment = self.current_event["Segments"][self.current_segment]
        for stage in segment["Stages"]:
            if stage["StageID"] == self.current_stage:
                for node_wrapper in stage.get("Nodes", []):
                    for node_type, node_data in node_wrapper.items():
                        if node_data.get("NodeID") == self.current_node:
                            # Создаем цель
                            goal_data = {}
                            if goal_type == "FixedGoal":
                                goal_data = {"Target": 10000}
                            elif goal_type == "ConsecutiveWinsGoal":
                                goal_data = {"Wins": 3, "Multiplier": 2.5, "Min": 1, "Max": 5}
                            elif goal_type == "SpinpadGoal":
                                goal_data = {"Spinpad": 100}
                            
                            node_data["Goal"] = {goal_type: goal_data}
                            break
                break
        
        self.update_event_tree()
        self.statusBar().showMessage(f'Добавлена цель типа: {goal_type}')
    
    def remove_goal(self):
        """Удалить текущую цель"""
        if not self.current_event or not self.current_segment or self.current_stage is None or self.current_node is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите цель для удаления")
            return
        
        # Находим узел
        segment = self.current_event["Segments"][self.current_segment]
        for stage in segment["Stages"]:
            if stage["StageID"] == self.current_stage:
                for node_wrapper in stage.get("Nodes", []):
                    for node_type, node_data in node_wrapper.items():
                        if node_data.get("NodeID") == self.current_node:
                            if "Goal" in node_data:
                                del node_data["Goal"]
                            break
                break
        
        self.update_event_tree()
        self.statusBar().showMessage('Цель удалена')
    
    def on_goal_selected(self, item):
        """Обработчик выбора цели"""
        goal_type = item.text()
        self.on_goal_type_changed(goal_type)
    
    def add_reward_dialog(self):
        """Диалог добавления награды"""
        if not self.current_event or not self.current_segment or self.current_stage is None or self.current_node is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите или создайте узел")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить награду")
        layout = QFormLayout(dialog)
        
        currency_combo = QComboBox()
        currency_combo.addItems(["Coins", "Gems", "EventCurrency", "Tickets"])
        layout.addRow("Валюта:", currency_combo)
        
        amount_spin = QDoubleSpinBox()
        amount_spin.setRange(0, 1000000000)
        amount_spin.setValue(1000)
        layout.addRow("Количество:", amount_spin)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QDialog.Accepted:
            currency = currency_combo.currentText()
            amount = amount_spin.value()
            self.add_reward(currency, amount)
    
    def add_reward(self, currency, amount):
        """Добавить награду"""
        if not self.current_event or not self.current_segment or self.current_stage is None or self.current_node is None:
            return
        
        # Находим узел
        segment = self.current_event["Segments"][self.current_segment]
        for stage in segment["Stages"]:
            if stage["StageID"] == self.current_stage:
                for node_wrapper in stage.get("Nodes", []):
                    for node_type, node_data in node_wrapper.items():
                        if node_data.get("NodeID") == self.current_node:
                            # Создаем награду
                            reward = {"FixedReward": {"Currency": currency, "Amount": amount}}
                            
                            if "Rewards" not in node_data:
                                node_data["Rewards"] = []
                            
                            node_data["Rewards"].append(reward)
                            break
                break
        
        self.update_event_tree()
        self.statusBar().showMessage(f'Добавлена награда: {currency} x {amount}')
    
    def remove_reward(self):
        """Удалить текущую награду"""
        if not self.current_event or not self.current_segment or self.current_stage is None or self.current_node is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите награду для удаления")
            return
        
        current_item = self.rewards_list.currentItem()
        if not current_item:
            return
        
        row = self.rewards_list.row(current_item)
        
        # Находим узел
        segment = self.current_event["Segments"][self.current_segment]
        for stage in segment["Stages"]:
            if stage["StageID"] == self.current_stage:
                for node_wrapper in stage.get("Nodes", []):
                    for node_type, node_data in node_wrapper.items():
                        if node_data.get("NodeID") == self.current_node:
                            if "Rewards" in node_data and 0 <= row < len(node_data["Rewards"]):
                                del node_data["Rewards"][row]
                            break
                break
        
        self.update_event_tree()
        self.statusBar().showMessage('Награда удалена')
    
    def on_reward_selected(self, item):
        """Обработчик выбора награды"""
        # Можно добавить загрузку данных награды для редактирования
        pass


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Устанавливаем стиль
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = LiveEventBuilderGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()