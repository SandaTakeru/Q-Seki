from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, cast

try:
    from qgis.core import QgsProject, QgsLayoutItemLabel, QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes
    from qgis.PyQt.QtCore import QObject, QSettings, Qt
    from qgis.PyQt.QtGui import QFont, QFontDatabase, QIcon
    from qgis.PyQt.QtWidgets import QAction, QApplication, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QPushButton, QCheckBox, QComboBox, QMenu, QListWidget, QAbstractItemView, QListWidgetItem
except ImportError:  # pragma: no cover
    QgsProject = None  # type: ignore
    QgsLayoutItemLabel = None  # type: ignore
    QgsLayoutPoint = None  # type: ignore
    QgsLayoutSize = None  # type: ignore
    QgsUnitTypes = None  # type: ignore
    QObject = object
    QSettings = None  # type: ignore
    Qt = None  # type: ignore
    QIcon = None  # type: ignore
    QFont = None  # type: ignore
    QFontDatabase = None  # type: ignore

    class _DummyClipboard:
        _text = ''

        def setText(self, value):
            self._text = '' if value is None else str(value)

        def text(self):
            return self._text

    class QApplication:
        _clipboard = _DummyClipboard()

        @classmethod
        def clipboard(cls):
            return cls._clipboard

        @classmethod
        def activeWindow(cls):
            return None

    class _Signal:
        def connect(self, callback):
            self._callback = callback

    class _DummyWidget:
        def __init__(self, *args, **kwargs):
            self.clicked = _Signal()
            self.triggered = _Signal()
            self.text_value = ''
            self.textChanged = _Signal()
            self.currentTextChanged = _Signal()
            self.toggled = _Signal()
            self._menu_actions = []
            self._enabled = True

        def setText(self, value):
            self.text_value = str(value)

        def text(self):
            return self.text_value

        def setReadOnly(self, *args, **kwargs):
            pass

        def setEnabled(self, enabled):
            self._enabled = bool(enabled)

        def isEnabled(self):
            return self._enabled

        def isChecked(self):
            return False

        def toggle(self, *args, **kwargs):
            pass

        def connect(self, callback):
            self._callback = callback

        def exec_(self):
            return 0

        def addWidget(self, *args, **kwargs):
            return None

        def addLayout(self, *args, **kwargs):
            return None

        def addStretch(self, *args, **kwargs):
            return None

        def addRow(self, *args, **kwargs):
            return None

        def clear(self):
            self.text_value = ''

        def addItems(self, *args, **kwargs):
            return None

        def addItem(self, *args, **kwargs):
            return None

        def setObjectName(self, *args, **kwargs):
            return None

        def objectName(self):
            return ''

        def addAction(self, action):
            self._menu_actions.append(action)
            return action

        def addMenu(self, *args, **kwargs):
            m = QMenu()
            self._menu_actions.append(m)
            return m

        def menuBar(self):
            return self

        def findChildren(self, *args, **kwargs):
            return list(self._menu_actions)

        def setWindowTitle(self, *args, **kwargs):
            return None

        def resize(self, *args, **kwargs):
            return None

        def setLayout(self, *args, **kwargs):
            return None

        def setIcon(self, *args, **kwargs):
            return None

        def accept(self):
            return None

    class QAction(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class QDialog(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class QFormLayout(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class QHBoxLayout(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class QLabel(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class QLineEdit(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if args:
                self.text_value = str(args[0])
        def setText(self, value):
            self.text_value = str(value)
            try:
                self.textChanged.connect  # type: ignore
            except Exception:
                pass

    class QVBoxLayout(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class QPushButton(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if args:
                self.text_value = str(args[0])

    class QCheckBox(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if args:
                self.text_value = str(args[0])

    class QComboBox(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._items: list[str] = []
            self._index = 0

        def addItems(self, items):
            for it in items:
                self.addItem(it)

        def addItem(self, item):
            self._items.append(str(item))

        def clear(self):
            self._items = []
            self._index = 0

        def currentText(self):
            if not self._items:
                return ''
            return self._items[self._index]

        def setCurrentIndex(self, i):
            try:
                self._index = int(i)
            except Exception:
                self._index = 0

        def items(self):
            return list(self._items)

    class _DummyListItem:
        def __init__(self, value: str):
            self._value = str(value)
            self._selected = False
            self._checked = False
            self._flags = 0

        def text(self):
            return self._value

        def setSelected(self, selected: bool):
            self._selected = bool(selected)

        def flags(self):
            return self._flags

        def setFlags(self, flags):
            self._flags = flags

        def setCheckState(self, state):
            self._checked = bool(state)

        def checkState(self):
            return 2 if self._checked else 0

    class QListWidgetItem(_DummyListItem):
        pass

    class QListWidget(_DummyWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._items: list[_DummyListItem] = []
            self._selected: set[int] = set()
            self.itemSelectionChanged = _Signal()
            self.itemChanged = _Signal()

        def addItems(self, items):
            for it in items:
                self.addItem(it)

        def addItem(self, item):
            if isinstance(item, _DummyListItem):
                self._items.append(item)
                return
            self._items.append(_DummyListItem(str(item)))

        def clear(self):
            self._items = []
            self._selected = set()

        def setSelectionMode(self, *args, **kwargs):
            return None

        def blockSignals(self, *args, **kwargs):
            return False

        def count(self):
            return len(self._items)

        def item(self, i):
            try:
                return self._items[int(i)]
            except Exception:
                return None

        def selectedItems(self):
            return [self._items[i] for i in sorted(self._selected) if 0 <= i < len(self._items)]

    class QAbstractItemView:
        MultiSelection = 3

    class QMenu(_DummyWidget):
        def __init__(self, title=''):
            super().__init__()
            self._title = str(title)

        def title(self):
            return self._title

        def addAction(self, action):
            self._menu_actions.append(action)
            return action

    QAction = QAction
    QDialog = QDialog
    QFormLayout = QFormLayout
    QHBoxLayout = QHBoxLayout
    QLabel = QLabel
    QLineEdit = QLineEdit
    QVBoxLayout = QVBoxLayout
    QPushButton = QPushButton
    QCheckBox = QCheckBox
    QComboBox = QComboBox
    QMenu = QMenu
    QListWidget = QListWidget
    QListWidgetItem = QListWidgetItem
    QAbstractItemView = QAbstractItemView

try:
    from .expression_functions import build_kyuseki_expression, kyuseki_html
except ImportError:  # pragma: no cover
    try:
        from expression_functions import build_kyuseki_expression, kyuseki_html
    except ImportError:  # pragma: no cover
        build_kyuseki_expression = None
        kyuseki_html = None


class KshExpressionBuilderDialog(QDialog):
    """kyuseki_html() の雛形を簡単に作るための簡易ダイアログ。"""

    _SETTINGS_GROUP = 'Q積表/ExpressionBuilder'
    _START_LABEL_TO_VALUE = {
        '北': 'north',
        '東': 'east',
        '南': 'south',
        '西': 'west',
    }
    _START_VALUE_TO_LABEL = {v: k for k, v in _START_LABEL_TO_VALUE.items()}
    _DEFAULT_LABEL_FONT_FAMILIES = (
        'BIZ UDGothic',
        'BIZ UDPGothic',
        'Noto Sans CJK JP',
        'Yu Gothic',
    )
    _DEFAULT_LABEL_FONT_SIZE_PT = 5.0

    def __init__(self, iface: Any | None = None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self._name_to_layer: dict[str, Any] = {}
        self._restoring_state = False
        self._settings = QSettings() if QSettings is not None else None
        self._saved_values = self._load_saved_values()
        self._filter_candidates_all: list[str] = []
        self._filter_checked_values: set[str] = set()
        self.setWindowTitle('Q積表 求積表の式作成')
        self.resize(680, 420)
        # レイヤ/フィールド選択は QGIS 実行時はコンボ、非実行時はテキスト
        if QgsProject is not None:
            self._layer_edit = QComboBox()
            self._filter_edit = QLineEdit('')
            self._filter_list = QListWidget()
            self._set_filter_list_multi_selection_mode()
            self._point_layer_edit = QComboBox()
            self._name_field_edit = QComboBox()
            self._label_field_edit = QComboBox()
            self._marker_field_edit = QComboBox()
        else:
            self._layer_edit = QLineEdit('境界')
            self._filter_edit = QLineEdit("")
            self._filter_list = None
            self._point_layer_edit = QLineEdit('点名レイヤ')
            self._name_field_edit = QLineEdit('点名')
            self._label_field_edit = QLineEdit('地番')
            self._marker_field_edit = QLineEdit('境界標')
        self._full_precision = QCheckBox('座標・計算値を丸めず計算・表示する')
        self._show_total_table = QCheckBox('合計欄を表示する')
        self._show_tsubo = QCheckBox('地積の下に坪を表示する')
        self._coord_digits_edit = QLineEdit('3')
        self._area_digits_edit = QLineEdit('2')
        self._tolerance_edit = QLineEdit('0.0005')
        self._column_count_edit = QLineEdit('1')
        self._start_edit = QComboBox() if QgsProject is not None else QLineEdit('北')
        if isinstance(self._start_edit, QComboBox):
            try:
                self._start_edit.addItems(list(self._START_LABEL_TO_VALUE.keys()))
            except Exception:
                pass
        self._copy_button = QPushButton('この式をコピー')
        self._insert_label_button = QPushButton('印刷レイアウトに追加')
        self._result_edit = QLineEdit('')
        self._result_edit.setReadOnly(True)

        form = QFormLayout()
        # QFormLayout が本物であれば addRow を使い、ダミーでは setText する
        try:
            form.addRow('求積対象のポリゴンレイヤ（必須）', self._layer_edit)
            form.addRow('地番の属性フィールド', self._label_field_edit)
            if self._filter_list is not None:
                form.addRow('対象の地番（複数選択可、空白で全選択）', self._filter_list)
            else:
                form.addRow('対象の地番（カンマ区切り）', self._filter_edit)
            form.addRow('筆界点のポイントレイヤ', self._point_layer_edit)
            form.addRow('点名の属性フィールド', self._name_field_edit)
            form.addRow('境界標の属性フィールド', self._marker_field_edit)
            form.addRow('フル桁計算', self._full_precision)
            form.addRow('座標の丸め後桁数', self._coord_digits_edit)
            form.addRow('地積の表示桁数', self._area_digits_edit)
            form.addRow('求積表の横並び列数', self._column_count_edit)
            form.addRow('合計欄', self._show_total_table)
            form.addRow('坪表示', self._show_tsubo)
            form.addRow('頂点の開始方向', self._start_edit)
            form.addRow('点名照合の許容距離', self._tolerance_edit)
        except Exception:
            # 非 GUI テスト時のダミー動作
            pass

        action_row = QHBoxLayout()
        action_row.addWidget(self._insert_label_button)
        action_row.addStretch()
        action_row.addWidget(self._copy_button)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(QLabel('作成される式（そのまま貼り付けできます）:'))
        layout.addWidget(self._result_edit)
        self._status_label = QLabel('')
        layout.addWidget(self._status_label)
        layout.addLayout(action_row)
        self.setLayout(layout)

        try:
            self._copy_button.clicked.connect(self._build_and_copy)
        except Exception:
            pass

        try:
            self._insert_label_button.clicked.connect(self._insert_label_into_layout)
        except Exception:
            pass

        # シグナル接続: QComboBox と QLineEdit の両方に対応
        try:
            if isinstance(self._layer_edit, QComboBox):
                # QGIS 環境ならレイヤ一覧を読み込む
                self._populate_layers()
                self._layer_edit.currentTextChanged.connect(self._on_polygon_layer_changed)
            else:
                self._layer_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            if isinstance(self._point_layer_edit, QComboBox):
                self._point_layer_edit.currentTextChanged.connect(self._on_point_layer_changed)
            else:
                self._point_layer_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            if isinstance(self._name_field_edit, QComboBox):
                self._name_field_edit.currentTextChanged.connect(self._refresh_preview)
            else:
                self._name_field_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            if isinstance(self._label_field_edit, QComboBox):
                self._label_field_edit.currentTextChanged.connect(self._on_label_field_changed)
            else:
                self._label_field_edit.textChanged.connect(self._on_label_field_changed)
        except Exception:
            pass

        try:
            if self._filter_list is None:
                self._filter_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            if self._filter_list is not None:
                # 複数選択UIは選択変更をトリガに反映する
                if hasattr(self._filter_list, 'itemSelectionChanged'):
                    self._filter_list.itemSelectionChanged.connect(self._on_filter_list_selection_changed)
                if hasattr(self._filter_list, 'itemChanged'):
                    self._filter_list.itemChanged.connect(self._on_filter_list_selection_changed)
        except Exception:
            pass

        try:
            self._full_precision.toggled.connect(self._refresh_preview)
        except Exception:
            pass
        try:
            self._full_precision.toggled.connect(self._update_precision_related_ui)
        except Exception:
            pass
        try:
            self._show_tsubo.toggled.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            self._show_total_table.toggled.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            self._coord_digits_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            self._area_digits_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            self._tolerance_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            self._column_count_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        try:
            if isinstance(self._start_edit, QComboBox):
                self._start_edit.currentTextChanged.connect(self._refresh_preview)
            else:
                self._start_edit.textChanged.connect(self._refresh_preview)
        except Exception:
            pass

        self._apply_saved_values()
        self._update_precision_related_ui()

        self._refresh_preview()

    def _update_precision_related_ui(self):
        """フル桁計算ON時は丸め関連入力を無効化する。"""
        is_full_precision = False
        try:
            if hasattr(self._full_precision, 'isChecked'):
                is_full_precision = bool(self._full_precision.isChecked())
        except Exception:
            is_full_precision = False

        editable = not is_full_precision
        for widget in (self._coord_digits_edit, self._area_digits_edit):
            try:
                if hasattr(widget, 'setEnabled'):
                    widget.setEnabled(editable)
            except Exception:
                pass

    def _load_saved_values(self) -> dict[str, str]:
        if self._settings is None:
            return {}
        keys = [
            'polygon_layer',
            'label_field',
            'feature_filter',
            'point_layer',
            'name_field',
            'marker_field',
            'full_precision',
            'coord_digits',
            'area_digits',
            'tolerance',
            'start',
            'show_total_table',
            'column_count',
            'show_tsubo',
        ]
        values: dict[str, str] = {}
        for key in keys:
            try:
                v = self._settings.value(f'{self._SETTINGS_GROUP}/{key}', '')
            except Exception:
                v = ''
            values[key] = '' if v is None else str(v)
        return values

    def _save_current_values(self) -> None:
        if self._settings is None:
            return
        values = {
            'polygon_layer': self._widget_text(self._layer_edit),
            'label_field': self._widget_text(self._label_field_edit),
            'feature_filter': self._current_filter_text(),
            'point_layer': self._widget_text(self._point_layer_edit),
            'name_field': self._widget_text(self._name_field_edit),
            'marker_field': self._widget_text(self._marker_field_edit),
            'full_precision': 'true' if self._full_precision.isChecked() else 'false',
            'coord_digits': self._widget_text(self._coord_digits_edit),
            'area_digits': self._widget_text(self._area_digits_edit),
            'tolerance': self._widget_text(self._tolerance_edit),
            'start': self._normalize_start_value(self._widget_text(self._start_edit)),
            'show_total_table': 'true' if self._show_total_table.isChecked() else 'false',
            'column_count': self._widget_text(self._column_count_edit),
            'show_tsubo': 'true' if self._show_tsubo.isChecked() else 'false',
        }
        for key, value in values.items():
            try:
                self._settings.setValue(f'{self._SETTINGS_GROUP}/{key}', value)
            except Exception:
                pass

    @staticmethod
    def _to_bool(value: str, default: bool = False) -> bool:
        text = str(value).strip().lower()
        if text in {'1', 'true', 'yes', 'on'}:
            return True
        if text in {'0', 'false', 'no', 'off'}:
            return False
        return default

    @staticmethod
    def _combo_items(combo: Any) -> list[str]:
        try:
            if hasattr(combo, 'count') and hasattr(combo, 'itemText'):
                return [str(combo.itemText(i)) for i in range(int(combo.count()))]
            if hasattr(combo, 'items'):
                return [str(v) for v in combo.items()]
        except Exception:
            return []
        return []

    @classmethod
    def _set_combo_value(cls, combo: Any, value: str, fallback: str = '') -> None:
        items = cls._combo_items(combo)
        if not items:
            return
        target = value if value in items else (fallback if fallback in items else items[0])
        try:
            if hasattr(combo, 'setCurrentText'):
                combo.setCurrentText(target)
                return
            idx = items.index(target)
            if hasattr(combo, 'setCurrentIndex'):
                combo.setCurrentIndex(idx)
        except Exception:
            pass

    @staticmethod
    def _set_checkbox(checkbox: Any, checked: bool) -> None:
        try:
            if hasattr(checkbox, 'setChecked'):
                checkbox.setChecked(bool(checked))
        except Exception:
            pass

    @classmethod
    def _normalize_start_value(cls, value: str) -> str:
        text = str(value).strip().lower()
        if text in cls._START_VALUE_TO_LABEL:
            return text
        jp = str(value).strip()
        return cls._START_LABEL_TO_VALUE.get(jp, 'north')

    @classmethod
    def _start_label_from_value(cls, value: str) -> str:
        normalized = cls._normalize_start_value(value)
        return cls._START_VALUE_TO_LABEL.get(normalized, '北')

    def _select_filter_list_from_filter_text(self, filter_text: str) -> None:
        if self._filter_list is None:
            return

        wanted = {v.strip() for v in str(filter_text).split(',') if v.strip()}
        if self._filter_candidates_all:
            wanted = {v for v in wanted if v in set(self._filter_candidates_all)}
        self._filter_checked_values = wanted
        self._rebuild_filter_list_items()
        self._sync_filter_edit_from_checked_values()

    def _current_filter_text(self) -> str:
        if self._filter_list is None:
            return self._widget_text(self._filter_edit)
        if not self._filter_checked_values:
            return ''
        order = {v: i for i, v in enumerate(self._filter_candidates_all)}
        ordered = sorted(self._filter_checked_values, key=lambda v: order.get(v, 10**9))
        return ','.join(ordered)

    def _sync_filter_edit_from_checked_values(self) -> None:
        text = self._current_filter_text()
        try:
            self._filter_edit.setText(text)
        except Exception:
            pass

    def _rebuild_filter_list_items(self) -> None:
        if self._filter_list is None:
            return

        try:
            if hasattr(self._filter_list, 'blockSignals'):
                self._filter_list.blockSignals(True)
        except Exception:
            pass

        try:
            self._filter_list.clear()
            # 地番JUMPに合わせ、空白項目 + 複数選択リストで操作する
            self._filter_list.addItem('')
            for value in self._filter_candidates_all:
                item = QListWidgetItem(str(value)) if QListWidgetItem is not None else str(value)
                self._filter_list.addItem(item)

            if hasattr(self._filter_list, 'count') and hasattr(self._filter_list, 'item'):
                for i in range(int(self._filter_list.count())):
                    item = self._filter_list.item(i)
                    if item is None:
                        continue
                    text = str(item.text())
                    if text and text in self._filter_checked_values and hasattr(item, 'setSelected'):
                        item.setSelected(True)

            if len(self._filter_candidates_all) == 1 and hasattr(self._filter_list, 'item'):
                auto_item = self._filter_list.item(1)
                if auto_item is not None and hasattr(auto_item, 'setSelected'):
                    auto_item.setSelected(True)
                    self._filter_checked_values = {str(auto_item.text())}
        finally:
            try:
                if hasattr(self._filter_list, 'blockSignals'):
                    self._filter_list.blockSignals(False)
            except Exception:
                pass

    def _apply_saved_values(self) -> None:
        if not self._saved_values:
            return

        self._restoring_state = True
        try:
            polygon_layer = self._saved_values.get('polygon_layer', '')
            if isinstance(self._layer_edit, QComboBox):
                self._set_combo_value(self._layer_edit, polygon_layer)
                self._on_polygon_layer_changed(self._widget_text(self._layer_edit))
            elif polygon_layer:
                self._layer_edit.setText(polygon_layer)

            label_field = self._saved_values.get('label_field', '')
            if isinstance(self._label_field_edit, QComboBox):
                self._set_combo_value(self._label_field_edit, label_field, fallback='地番')
            elif label_field:
                self._label_field_edit.setText(label_field)
            self._on_label_field_changed()

            point_layer = self._saved_values.get('point_layer', '')
            if isinstance(self._point_layer_edit, QComboBox):
                self._set_combo_value(self._point_layer_edit, point_layer)
                self._on_point_layer_changed(self._widget_text(self._point_layer_edit))
            else:
                self._point_layer_edit.setText(point_layer)

            name_field = self._saved_values.get('name_field', '')
            if isinstance(self._name_field_edit, QComboBox):
                self._set_combo_value(self._name_field_edit, name_field, fallback='点名')
            elif name_field:
                self._name_field_edit.setText(name_field)

            marker_field = self._saved_values.get('marker_field', '')
            if isinstance(self._marker_field_edit, QComboBox):
                self._set_combo_value(self._marker_field_edit, marker_field, fallback='境界標')
            elif marker_field:
                self._marker_field_edit.setText(marker_field)

            filter_text = self._saved_values.get('feature_filter', '')
            self._select_filter_list_from_filter_text(filter_text)

            coord_digits = self._saved_values.get('coord_digits', '')
            area_digits = self._saved_values.get('area_digits', '')
            tolerance = self._saved_values.get('tolerance', '')
            column_count = self._saved_values.get('column_count', '')

            if coord_digits:
                self._coord_digits_edit.setText(coord_digits)
            if area_digits:
                self._area_digits_edit.setText(area_digits)
            if tolerance:
                self._tolerance_edit.setText(tolerance)
            if column_count:
                self._column_count_edit.setText(column_count)

            start = self._saved_values.get('start', '')
            if isinstance(self._start_edit, QComboBox):
                self._set_combo_value(self._start_edit, self._start_label_from_value(start), fallback='北')
            elif start:
                self._start_edit.setText(self._start_label_from_value(start))

            self._set_checkbox(self._full_precision, self._to_bool(self._saved_values.get('full_precision', 'false')))
            self._set_checkbox(self._show_total_table, self._to_bool(self._saved_values.get('show_total_table', 'false')))
            self._set_checkbox(self._show_tsubo, self._to_bool(self._saved_values.get('show_tsubo', 'false')))
        finally:
            self._restoring_state = False

    @staticmethod
    def _to_int(value: str, default: int) -> int:
        try:
            return int(str(value).strip())
        except Exception:
            return default

    @staticmethod
    def _to_float(value: str, default: float) -> float:
        try:
            return float(str(value).strip())
        except Exception:
            return default

    def _set_filter_list_multi_selection_mode(self) -> None:
        if self._filter_list is None:
            return
        # PyQt バージョン差異を吸収して複数選択モードを設定
        candidates = [
            getattr(QAbstractItemView, 'MultiSelection', None),
            getattr(QAbstractItemView, 'ExtendedSelection', None),
        ]
        selection_mode_enum = getattr(QAbstractItemView, 'SelectionMode', None)
        if selection_mode_enum is not None:
            candidates.extend([
                getattr(selection_mode_enum, 'MultiSelection', None),
                getattr(selection_mode_enum, 'ExtendedSelection', None),
            ])

        for mode in candidates:
            if mode is None:
                continue
            try:
                self._filter_list.setSelectionMode(mode)
                return
            except Exception:
                continue

    @staticmethod
    def _sort_chiban_key(value: str):
        """地番を若い順に並べるためのキー（例: 2-9 < 2-10）。"""
        text = str(value)
        if text == 'NULL':
            return (0, [])

        parts = text.split('-')
        key = []
        for part in parts:
            p = part.strip()
            if p.isdigit():
                key.append((0, int(p)))
            else:
                key.append((1, p))
        return (1, key, text)

    def _populate_layers(self):
        """QGIS 実行時にプロジェクトのレイヤとフィールドを読み込む。"""
        if QgsProject is None:
            return
        project = QgsProject.instance()
        layers = list(project.mapLayers().values())
        poly_names = []
        point_names = []
        poly_layers = []
        for layer in layers:
            try:
                geom_type = layer.geometryType()
            except Exception:
                geom_type = None
            # geometryType: 0=point,1=line,2=polygon
            if geom_type == 2:
                poly_names.append(layer.name())
                poly_layers.append(layer)
            if geom_type == 0:
                point_names.append(layer.name())

        try:
            self._layer_edit.clear()
            self._layer_edit.addItems(poly_names)
            self._point_layer_edit.clear()
            self._point_layer_edit.addItems(point_names)
        except Exception:
            pass
        # 初期フィールドは先頭ポリゴンレイヤに合わせる
        if poly_layers:
            try:
                self._populate_fields_for_layer(poly_layers[0])
                self._populate_filter_values(poly_layers[0])
            except Exception:
                pass
        if point_names:
            try:
                first_point = point_names[0]
                point_layer = next((l for l in layers if l.name() == first_point), None)
                if point_layer is not None:
                    self._populate_point_fields(point_layer)
            except Exception:
                pass

        # name->layer マップを保持
        try:
            self._name_to_layer = {l.name(): l for l in layers}
        except Exception:
            self._name_to_layer = {}

    def _on_polygon_layer_changed(self, name: str):
        """ポリゴンレイヤが選択されたときにフィールドと絞り値を更新する。"""
        layer = None
        try:
            layer = self._name_to_layer.get(name)
        except Exception:
            layer = None
        if layer is not None:
            try:
                self._populate_fields_for_layer(layer)
                self._populate_filter_values(layer)
            except Exception:
                pass
        self._refresh_preview()

    def _on_point_layer_changed(self, name: str):
        """ポイントレイヤが選択されたときに点名フィールドを更新する。"""
        layer = None
        try:
            layer = self._name_to_layer.get(name)
        except Exception:
            layer = None
        if layer is not None:
            try:
                self._populate_point_fields(layer)
            except Exception:
                pass
        self._refresh_preview()

    def _on_label_field_changed(self, *args, **kwargs):
        """地番属性変更時に、絞り込み候補を該当属性へ連動させる。"""
        layer = None
        try:
            layer_name = self._widget_text(self._layer_edit)
            layer = self._name_to_layer.get(layer_name)
        except Exception:
            layer = None
        if layer is not None:
            try:
                self._populate_filter_values(layer)
            except Exception:
                pass
        self._refresh_preview()

    def _on_filter_list_selection_changed(self):
        """候補リストの複数選択値を feature_filter へカンマ連結で反映する。"""
        if self._restoring_state:
            return
        if self._filter_list is None:
            return

        checked_values: set[str] = set()
        try:
            selected = self._filter_list.selectedItems()
            for item in selected:
                try:
                    value = str(item.text())
                    if value:
                        checked_values.add(value)
                except Exception:
                    continue
        except Exception:
            pass
        self._filter_checked_values = checked_values
        self._sync_filter_edit_from_checked_values()
        self._refresh_preview()

    def _populate_filter_values(self, layer):
        """選択したポリゴンレイヤから地番候補を抽出して filter コンボに入れる。"""
        if QgsProject is None:
            return
        try:
            candidates = ['地番', '地番1', '地番2']
            fields = [f.name() for f in layer.fields()]
            selected_label = self._widget_text(self._label_field_edit).strip()
            chosen = selected_label if selected_label in fields else None
            if chosen is None:
                for c in candidates:
                    if c in fields:
                        chosen = c
                        break
            if chosen is None and fields:
                chosen = fields[0]

            values = set()
            for feat in layer.getFeatures():
                try:
                    v = feat[chosen]
                    if v is not None:
                        values.add(str(v))
                except Exception:
                    continue
            sorted_vals = sorted(values, key=self._sort_chiban_key)
            previous_checked = set(self._filter_checked_values)
            self._filter_candidates_all = sorted_vals
            self._filter_checked_values = {v for v in previous_checked if v in set(sorted_vals)}
            if self._filter_list is not None:
                try:
                    self._rebuild_filter_list_items()
                    self._sync_filter_edit_from_checked_values()
                except Exception:
                    pass
        except Exception:
            pass

    @staticmethod
    def _widget_text(widget) -> str:
        try:
            if hasattr(widget, 'currentText'):
                return str(widget.currentText())
            if hasattr(widget, 'text'):
                return str(widget.text())
        except Exception:
            return ''
        return ''

    def _populate_fields_for_layer(self, layer):
        try:
            fields = [f.name() for f in layer.fields()]
            try:
                # polygon layer -> label field
                try:
                    self._label_field_edit.clear()
                    self._label_field_edit.addItems(fields)
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass

    def _populate_point_fields(self, layer):
        """ポイントレイヤのフィールドを点名フィールドコンボに入れる。"""
        try:
            fields = [f.name() for f in layer.fields()]
            try:
                self._name_field_edit.clear()
                self._name_field_edit.addItems(fields)
            except Exception:
                pass
            try:
                self._marker_field_edit.clear()
                self._marker_field_edit.addItems(fields)
            except Exception:
                pass
        except Exception:
            pass

    def _refresh_preview(self):
        if build_kyuseki_expression is None:
            self._result_edit.setText('')
            return
        layer_val = self._widget_text(self._layer_edit)
        filter_val = self._current_filter_text()
        point_layer_val = self._widget_text(self._point_layer_edit)
        name_field_val = self._widget_text(self._name_field_edit) or '点名'
        label_field_val = self._widget_text(self._label_field_edit) or '地番'
        marker_field_val = self._widget_text(self._marker_field_edit) or '境界標'
        coord_digits_val = self._to_int(self._widget_text(self._coord_digits_edit), 3)
        area_digits_val = self._to_int(self._widget_text(self._area_digits_edit), 2)
        tolerance_val = self._to_float(self._widget_text(self._tolerance_edit), 0.0005)
        start_val = self._normalize_start_value(self._widget_text(self._start_edit) or 'north')
        column_count_val = self._to_int(self._widget_text(self._column_count_edit), 1)

        text = build_kyuseki_expression(
            layer_val,
            label_field_val,
            filter_val,
            point_layer_val,
            name_field_val,
            marker_field_val,
            self._full_precision.isChecked() if hasattr(self._full_precision, 'isChecked') else False,
            coord_digits_val,
            area_digits_val,
            column_count_val,
            self._show_total_table.isChecked() if hasattr(self._show_total_table, 'isChecked') else False,
            self._show_tsubo.isChecked() if hasattr(self._show_tsubo, 'isChecked') else False,
            start_val,
            tolerance_val,
        )
        self._result_edit.setText(text)

    def _build_and_copy(self):
        self._refresh_preview()
        expression = self._result_edit.text()
        if not expression:
            self._set_status('式が空のためコピーできませんでした。')
            return
        self._save_current_values()
        if self._set_clipboard_text(expression):
            self._set_status('式をクリップボードにコピーしました。')
        else:
            self._set_status('クリップボードへコピーできませんでした。')

    def _set_status(self, text: str) -> None:
        try:
            self._status_label.setText(str(text))
        except Exception:
            pass

    def _set_clipboard_text(self, text: str) -> bool:
        copied = False
        try:
            cb = QApplication.clipboard() if QApplication is not None else None
            if cb is not None and hasattr(cb, 'setText'):
                cb.setText(str(text))
                copied = True
        except Exception:
            copied = False

        if not copied and self.iface is not None and hasattr(self.iface, 'clipboard'):
            try:
                self.iface.clipboard().setText(str(text))
                copied = True
            except Exception:
                copied = False

        return copied

    def _iter_layout_designers(self) -> list[Any]:
        if self.iface is None:
            return []

        designers: list[Any] = []
        seen: set[int] = set()

        def _add(candidate: Any) -> None:
            if candidate is None:
                return
            ident = id(candidate)
            if ident in seen:
                return
            seen.add(ident)
            designers.append(candidate)

        for attr_name in ('activeLayoutDesignerInterface', 'layoutDesignerInterface'):
            try:
                getter = getattr(self.iface, attr_name, None)
                candidate = getter() if callable(getter) else None
                _add(candidate)
            except Exception:
                continue

        for attr_name in ('openLayoutDesigners', 'layoutDesigners', 'layoutDesignerInterfaces'):
            try:
                getter = getattr(self.iface, attr_name, None)
                values = getter() if callable(getter) else None
                if values is None:
                    continue
                for candidate in cast(Iterable[Any], values):
                    _add(candidate)
            except Exception:
                continue

        return designers

    @staticmethod
    def _designer_window(designer: Any) -> Any | None:
        if designer is None:
            return None
        if hasattr(designer, 'menuBar'):
            return designer
        try:
            if hasattr(designer, 'window'):
                wnd = designer.window()
                if wnd is not None:
                    return wnd
        except Exception:
            pass
        try:
            if hasattr(designer, 'mainWindow'):
                wnd = designer.mainWindow()
                if wnd is not None:
                    return wnd
        except Exception:
            pass
        return None

    def _resolve_layout_designer(self) -> Any | None:
        designers = self._iter_layout_designers()
        if not designers:
            return None

        active_window = None
        try:
            active_window = QApplication.activeWindow() if QApplication is not None else None
        except Exception:
            active_window = None

        if active_window is not None:
            for designer in designers:
                try:
                    if self._designer_window(designer) == active_window:
                        return designer
                except Exception:
                    continue

        return designers[0]

    def _insert_label_into_layout(self):
        """現在の印刷レイアウトに式入りラベルを追加する。"""
        self._refresh_preview()
        expression = self._result_edit.text()
        self._save_current_values()
        if not expression or self.iface is None:
            self._set_status('式が空のため追加できませんでした。')
            return

        if QgsLayoutItemLabel is None or QgsLayoutPoint is None or QgsUnitTypes is None:
            self._build_and_copy()
            self._set_status('レイアウトAPIが利用できないため、式のみコピーしました。')
            return

        try:
            designer = self._resolve_layout_designer()
            if designer is None:
                self._set_status('印刷レイアウト画面が見つかりませんでした。')
                return

            layout = designer.layout() if hasattr(designer, 'layout') else None
            if layout is None:
                self._set_status('現在のレイアウトが取得できませんでした。')
                return

            label = QgsLayoutItemLabel(layout)
            self._enable_label_html_mode(label)
            self._apply_default_label_font(label)
            label.setText(f'[% {expression} %]')
            try:
                label.setCustomProperty('kyuseki_item', True)
            except Exception:
                pass
            layout.addLayoutItem(label)
            try:
                if hasattr(label, 'adjustSizeToText'):
                    label.adjustSizeToText()
            except Exception:
                pass
            self._place_label_centered_within_current_page(designer, layout, label)
            try:
                if hasattr(layout, 'refresh'):
                    layout.refresh()
            except Exception:
                pass
            try:
                if hasattr(designer, 'selectItem'):
                    designer.selectItem(label)
            except Exception:
                pass
            self._set_status('印刷レイアウトへ求積表ラベルを追加しました。')
        except Exception:
            self._set_status('ラベル追加に失敗しました。式はコピーをお試しください。')
            return

    def _enable_label_html_mode(self, label: Any) -> None:
        """QgsLayoutItemLabel の HTML レンダリングを有効化する。"""
        if label is None:
            return

        # QGIS バージョン差異に備えて複数パターンを順に試す
        mode_candidates: list[Any] = []
        try:
            mode_candidates.append(getattr(QgsLayoutItemLabel, 'ModeHtml', None))
        except Exception:
            pass
        try:
            mode_enum = getattr(QgsLayoutItemLabel, 'Mode', None)
            if mode_enum is not None:
                mode_candidates.append(getattr(mode_enum, 'ModeHtml', None))
                mode_candidates.append(getattr(mode_enum, 'Html', None))
        except Exception:
            pass

        for mode in mode_candidates:
            if mode is None:
                continue
            try:
                if hasattr(label, 'setMode'):
                    label.setMode(mode)
                    return
            except Exception:
                continue

        # 最後のフォールバック: データ定義プロパティ経由やUI初期状態判定の補助フラグ
        try:
            label.setCustomProperty('htmlState', True)
        except Exception:
            pass

    def _apply_default_label_font(self, label: Any) -> None:
        """ラベルの初期フォントを設定する（BIZ UDGothic 優先、5pt）。"""
        if label is None or QFont is None:
            return

        font = None
        # まずは和文可読性重視の既定フォントを優先
        preferred_families = list(self._DEFAULT_LABEL_FONT_FAMILIES)

        available_families: set[str] = set()
        try:
            if QFontDatabase is not None:
                db = QFontDatabase()
                if hasattr(db, 'families'):
                    available_families = {str(name) for name in db.families()}
        except Exception:
            available_families = set()

        for family in preferred_families:
            if available_families and family not in available_families:
                continue
            try:
                preferred_font = QFont(family)
                if hasattr(preferred_font, 'setStyleStrategy'):
                    no_merge = getattr(QFont, 'NoFontMerging', None)
                    if no_merge is not None:
                        preferred_font.setStyleStrategy(no_merge)
                font = preferred_font
                break
            except Exception:
                continue

        try:
            if font is None and QFontDatabase is not None and hasattr(QFontDatabase, 'systemFont') and hasattr(QFontDatabase, 'FixedFont'):
                font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        except Exception:
            pass

        if font is None:
            try:
                font = QFont('Monospace')
                if hasattr(font, 'setStyleHint'):
                    # QFont.StyleHint.TypeWriter を優先し、なければ TypeWriter 相当を利用
                    style_hint = getattr(QFont, 'TypeWriter', None)
                    if style_hint is not None:
                        font.setStyleHint(style_hint)
            except Exception:
                font = None

        if font is None:
            return

        try:
            if hasattr(font, 'setPointSizeF'):
                font.setPointSizeF(float(self._DEFAULT_LABEL_FONT_SIZE_PT))
            elif hasattr(font, 'setPointSize'):
                font.setPointSize(int(round(self._DEFAULT_LABEL_FONT_SIZE_PT)))
        except Exception:
            pass

        try:
            if hasattr(label, 'setFont'):
                label.setFont(font)
        except Exception:
            pass

    def _layout_rect_from_page(self, page: Any) -> tuple[float, float, float, float] | None:
        """ページのレイアウト座標系矩形を取得する。"""
        if page is None:
            return None

        # 優先: pageRect() があれば原点+サイズを直接取得
        try:
            if hasattr(page, 'pageRect'):
                rect = page.pageRect()
                if rect is not None and hasattr(rect, 'x') and hasattr(rect, 'y') and hasattr(rect, 'width') and hasattr(rect, 'height'):
                    return (float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height()))
        except Exception:
            pass

        # 互換: pagePositionWithUnits + pageSizeWithUnits
        try:
            pos = page.pagePositionWithUnits() if hasattr(page, 'pagePositionWithUnits') else None
            size = page.pageSizeWithUnits() if hasattr(page, 'pageSizeWithUnits') else None
            if pos is not None and size is not None:
                return (float(pos.x()), float(pos.y()), float(size.width()), float(size.height()))
        except Exception:
            pass

        # 互換: pageSize()（単一ページ前提で原点(0,0)）
        try:
            size = page.pageSize() if hasattr(page, 'pageSize') else None
            if size is not None and hasattr(size, 'width') and hasattr(size, 'height'):
                return (0.0, 0.0, float(size.width()), float(size.height()))
        except Exception:
            pass

        return None

    def _current_view_center(self, designer: Any) -> tuple[float, float] | None:
        """現在表示中レイアウトビューの中心座標を取得する。"""
        if designer is None:
            return None
        try:
            view = designer.view() if hasattr(designer, 'view') else None
            if view is None or not hasattr(view, 'viewport') or not hasattr(view, 'mapToScene'):
                return None
            vp = view.viewport()
            if vp is None or not hasattr(vp, 'rect'):
                return None
            center = vp.rect().center()
            scene_pt = view.mapToScene(center)
            if scene_pt is None:
                return None
            return (float(scene_pt.x()), float(scene_pt.y()))
        except Exception:
            return None

    def _label_size_mm(self, label: Any) -> tuple[float, float]:
        """ラベルの現在サイズ(mm想定)を取得する。"""
        try:
            if hasattr(label, 'rect'):
                rect = label.rect()
                if rect is not None and hasattr(rect, 'width') and hasattr(rect, 'height'):
                    return (max(1.0, float(rect.width())), max(1.0, float(rect.height())))
        except Exception:
            pass
        return (80.0, 40.0)

    def _attempt_move_mm(self, label: Any, x: float, y: float) -> None:
        point_ctor = QgsLayoutPoint
        unit_mm = getattr(QgsUnitTypes, 'LayoutMillimeters', None)
        if point_ctor is None or unit_mm is None:
            return
        try:
            label.attemptMove(point_ctor(float(x), float(y), unit_mm))
        except Exception:
            pass

    def _attempt_resize_mm(self, label: Any, width: float, height: float) -> None:
        size_ctor = QgsLayoutSize
        unit_mm = getattr(QgsUnitTypes, 'LayoutMillimeters', None)
        if size_ctor is None or unit_mm is None:
            return
        try:
            label.attemptResize(size_ctor(float(width), float(height), unit_mm))
        except Exception:
            pass

    def _place_label_centered_within_current_page(self, designer: Any, layout: Any, label: Any) -> None:
        """表示中中心に配置しつつ、ページサイズ上限内へ収める。"""
        if label is None or layout is None:
            return

        page_rect = None
        try:
            page_collection = layout.pageCollection() if hasattr(layout, 'pageCollection') else None
            if page_collection is not None and hasattr(page_collection, 'pageCount') and int(page_collection.pageCount()) > 0:
                center = self._current_view_center(designer)
                target_page = None
                if center is not None and hasattr(page_collection, 'pageNumberForPoint'):
                    try:
                        point_ctor = QgsLayoutPoint
                        unit_mm = getattr(QgsUnitTypes, 'LayoutMillimeters', None)
                        if point_ctor is None or unit_mm is None:
                            raise RuntimeError('Layout point constructor unavailable')
                        page_index = int(page_collection.pageNumberForPoint(point_ctor(center[0], center[1], unit_mm)))
                        if page_index >= 0 and hasattr(page_collection, 'page'):
                            target_page = page_collection.page(page_index)
                    except Exception:
                        target_page = None
                if target_page is None and hasattr(page_collection, 'page'):
                    target_page = page_collection.page(0)
                page_rect = self._layout_rect_from_page(target_page)
        except Exception:
            page_rect = None

        if page_rect is None:
            # 最低限のフォールバック
            self._attempt_move_mm(label, 20.0, 20.0)
            return

        page_x, page_y, page_w, page_h = page_rect
        margin_mm = 6.0
        max_w = max(20.0, page_w - margin_mm * 2.0)
        max_h = max(20.0, page_h - margin_mm * 2.0)

        cur_w, cur_h = self._label_size_mm(label)
        target_w = min(cur_w, max_w)
        target_h = min(cur_h, max_h)

        if target_w < cur_w or target_h < cur_h:
            self._attempt_resize_mm(label, target_w, target_h)
            target_w, target_h = self._label_size_mm(label)

        center = self._current_view_center(designer)
        if center is None:
            center_x = page_x + page_w / 2.0
            center_y = page_y + page_h / 2.0
        else:
            center_x, center_y = center

        x = center_x - target_w / 2.0
        y = center_y - target_h / 2.0
        x = max(page_x + margin_mm, min(x, page_x + page_w - margin_mm - target_w))
        y = max(page_y + margin_mm, min(y, page_y + page_h - margin_mm - target_h))

        self._attempt_move_mm(label, x, y)


class KshLayoutAutoRefresh(QObject):
    """レイアウト HTML アイテムの自動更新を担当する。"""

    def __init__(self, iface: Any | None = None):
        super().__init__()
        self.iface = iface
        self._layer_refs: list[Any] = []

    def install(self) -> None:
        """更新フックを登録する。"""
        if QgsProject is None:
            return
        project = QgsProject.instance()
        project.layersAdded.connect(self._on_project_layers_changed)
        project.layersRemoved.connect(self._on_project_layers_changed)
        self._connect_project_layers()

    def uninstall(self) -> None:
        """更新フックを解除する。"""
        if QgsProject is None:
            return
        project = QgsProject.instance()
        try:
            project.layersAdded.disconnect(self._on_project_layers_changed)
        except Exception:
            pass
        try:
            project.layersRemoved.disconnect(self._on_project_layers_changed)
        except Exception:
            pass
        for layer in list(self._layer_refs):
            try:
                layer.layerModified.disconnect(self._on_layer_changed)
            except Exception:
                pass
            try:
                layer.geometryChanged.disconnect(self._on_layer_changed)
            except Exception:
                pass
            try:
                layer.editingStopped.disconnect(self._on_layer_changed)
            except Exception:
                pass
        self._layer_refs.clear()

    def _on_project_layers_changed(self, *args, **kwargs) -> None:
        self._connect_project_layers()
        self.refresh_html_items()

    def _connect_project_layers(self) -> None:
        if QgsProject is None:
            return
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            if layer in self._layer_refs:
                continue
            try:
                layer.layerModified.connect(self._on_layer_changed)
            except Exception:
                pass
            try:
                layer.geometryChanged.connect(self._on_layer_changed)
            except Exception:
                pass
            try:
                layer.editingStopped.connect(self._on_layer_changed)
            except Exception:
                pass
            self._layer_refs.append(layer)

    def _on_layer_changed(self, *args, **kwargs) -> None:
        """レイヤ変更時に関連テキストアイテムを更新する。"""
        self.refresh_html_items()

    def refresh_html_items(self) -> None:
        """レイアウト内の kyuseki_html() 利用項目（HTML/ラベル）を更新する。"""
        if QgsProject is None:
            return
        project = QgsProject.instance()
        for layout in list(project.layoutManager().layouts()):
            for item in layout.items():
                source = ''
                text = ''
                try:
                    if hasattr(item, 'htmlSource'):
                        source = item.htmlSource() or ''
                except Exception:
                    source = ''
                try:
                    if hasattr(item, 'text'):
                        text = item.text() or ''
                except Exception:
                    text = ''

                if (
                    'kyuseki_html(' in source
                    or 'kyuseki_html(' in text
                    or bool(item.customProperty('kyuseki_item', False))
                ):
                    try:
                        item.refresh()
                    except Exception:
                        pass


class KshPlugin:
    """QGIS プラグインの本体クラス。"""

    def __init__(self, iface: Any | None = None):
        self.iface = iface
        self.auto_refresh = KshLayoutAutoRefresh(iface)
        self.registered = False
        self.layout_action = None
        self._layout_designer_signal_connected = False
        self.icon_path = str(Path(__file__).resolve().parent / 'icon.svg')

    def initGui(self) -> None:
        """UI 初期化。"""
        self._register_expression_functions()
        self.auto_refresh.install()
        self._register_layout_designer_action()
        self.registered = True

    def _register_expression_functions(self) -> None:
        """QGIS の式関数として kyuseki_html を登録する。"""
        if kyuseki_html is None:
            return
        try:
            from qgis.core import QgsExpression
            try:
                if kyuseki_html is not None:
                    # 既存登録があれば一度解除し、引数メタデータを最新化する
                    try:
                        QgsExpression.unregisterFunction('kyuseki_html')
                    except Exception:
                        pass
                    QgsExpression.registerFunction(kyuseki_html)
            except Exception:
                pass
        except ImportError:
            pass

    def _register_layout_designer_action(self) -> None:
        """印刷レイアウト画面に専用アクションを追加する。"""
        if self.iface is None:
            return
        if self._layout_designer_signal_connected:
            return
        try:
            if hasattr(self.iface, 'layoutDesignerOpened'):
                self.iface.layoutDesignerOpened.connect(self._on_layout_designer_opened)
                self._layout_designer_signal_connected = True
        except Exception:
            pass

        # 既に開いているレイアウトデザイナにも注入する
        for designer in self._iter_layout_designers():
            self._on_layout_designer_opened(designer)

    def _iter_layout_designers(self) -> list[Any]:
        """現在取得可能なレイアウトデザイナを列挙する。"""
        if self.iface is None:
            return []

        designers: list[Any] = []
        seen: set[int] = set()

        def _add_candidate(candidate: Any) -> None:
            if candidate is None:
                return
            ident = id(candidate)
            if ident in seen:
                return
            seen.add(ident)
            designers.append(candidate)

        for attr_name in ('activeLayoutDesignerInterface', 'layoutDesignerInterface'):
            try:
                getter = getattr(self.iface, attr_name, None)
                candidate = getter() if callable(getter) else None
                _add_candidate(candidate)
            except Exception:
                continue

        for attr_name in ('openLayoutDesigners', 'layoutDesigners', 'layoutDesignerInterfaces'):
            try:
                getter = getattr(self.iface, attr_name, None)
                values = getter() if callable(getter) else None
                if values is None:
                    continue
                for candidate in cast(Iterable[Any], values):
                    _add_candidate(candidate)
            except Exception:
                continue

        return designers

    def _resolve_designer_window(self, designer: Any) -> Any | None:
        """レイアウトデザイナからウィンドウオブジェクトを取得する。"""
        if designer is None:
            return None
        if hasattr(designer, 'menuBar'):
            return designer
        try:
            if hasattr(designer, 'window'):
                wnd = designer.window()
                if wnd is not None:
                    return wnd
        except Exception:
            pass
        try:
            if hasattr(designer, 'mainWindow'):
                wnd = designer.mainWindow()
                if wnd is not None:
                    return wnd
        except Exception:
            pass
        return None

    def _find_ksh_menu(self, menu_bar: Any) -> Any | None:
        """メニューバー上の Q積表 メニューを探す。"""
        if menu_bar is None:
            return None

        try:
            for action in menu_bar.actions():
                menu = action.menu() if hasattr(action, 'menu') else None
                if menu is not None and hasattr(menu, 'title') and menu.title() == 'Q積表':
                    return menu
        except Exception:
            pass

        try:
            for menu in menu_bar.findChildren(QMenu):
                if menu.title() == 'Q積表':
                    return menu
        except Exception:
            pass

        return None

    def _on_layout_designer_opened(self, designer) -> None:
        """レイアウトデザイナ起動時に Q積表 メニューを注入する。"""
        if designer is None or QAction is None:
            return
        try:
            window = self._resolve_designer_window(designer)
            if window is None or not hasattr(window, 'menuBar'):
                return
            menu_bar = window.menuBar()
            if menu_bar is None:
                return

            target_menu = self._find_ksh_menu(menu_bar)
            if target_menu is None:
                target_menu = menu_bar.addMenu('Q積表')

            try:
                for existing_action in target_menu.actions():
                    if existing_action.objectName() == 'kshExpressionBuilderAction':
                        self.layout_action = existing_action
                        return
            except Exception:
                pass

            action = QAction('求積表ラベルを追加', window)
            action.setObjectName('kshExpressionBuilderAction')
            try:
                if QIcon is not None:
                    action.setIcon(QIcon(self.icon_path))
            except Exception:
                pass
            action.triggered.connect(self._show_expression_builder)
            target_menu.addAction(action)
            self.layout_action = action
        except Exception:
            pass

    def _show_expression_builder(self, *args, **kwargs) -> None:
        """簡易ダイアログを表示する。"""
        if QDialog is None:
            return

        candidate_parents: list[Any] = []
        seen: set[int] = set()

        def _push_parent(obj: Any) -> None:
            ident = id(obj)
            if ident in seen:
                return
            seen.add(ident)
            candidate_parents.append(obj)

        for designer in self._iter_layout_designers():
            window = self._resolve_designer_window(designer)
            if window is not None:
                _push_parent(window)

        try:
            if self.iface and hasattr(self.iface, 'mainWindow'):
                _push_parent(self.iface.mainWindow())
        except Exception:
            pass

        _push_parent(None)

        last_error = None
        for parent in candidate_parents:
            try:
                dialog = KshExpressionBuilderDialog(self.iface, parent)
                if hasattr(dialog, 'exec'):
                    dialog.exec()
                else:
                    dialog.exec_()
                return
            except Exception as e:
                last_error = e
                continue

        try:
            if self.iface is not None and hasattr(self.iface, 'messageBar'):
                self.iface.messageBar().pushWarning('Q積表', f'ダイアログの表示に失敗しました: {last_error}')
        except Exception:
            pass

    def unload(self) -> None:
        """プラグイン終了時の処理。"""
        self.auto_refresh.uninstall()
        try:
            from qgis.core import QgsExpression
            try:
                QgsExpression.unregisterFunction('kyuseki_html')
            except Exception:
                pass
        except ImportError:
            pass
        if self.iface is not None and self._layout_designer_signal_connected:
            try:
                self.iface.layoutDesignerOpened.disconnect(self._on_layout_designer_opened)
            except Exception:
                pass
            self._layout_designer_signal_connected = False
        self.registered = False


__all__ = ["KshPlugin", "KshLayoutAutoRefresh", "KshExpressionBuilderDialog", "kyuseki_html"]
