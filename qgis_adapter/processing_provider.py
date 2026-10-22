from __future__ import annotations

from typing import Any

try:
    from qgis.core import (
        QgsProcessingAlgorithm,
        QgsProcessingException,
        QgsProcessingParameterFeatureSource,
        QgsProcessingParameterField,
        QgsProcessingParameterString,
        QgsProcessingParameterVectorDestination,
        QgsProcessingOutputVectorLayer,
    )
except ImportError:  # pragma: no cover
    class QgsProcessingAlgorithm:  # type: ignore
        pass

    class QgsProcessingException(Exception):
        pass

    def _missing(*args, **kwargs):
        raise RuntimeError('QGIS Processing is not available in this environment.')

    QgsProcessingParameterFeatureSource = _missing
    QgsProcessingParameterField = _missing
    QgsProcessingParameterString = _missing
    QgsProcessingParameterVectorDestination = _missing
    QgsProcessingOutputVectorLayer = _missing


class KshCreateSurveyTableLayer(QgsProcessingAlgorithm):
    """求積表レイヤ生成の Processing アルゴリズム。"""

    INPUT = 'INPUT'
    LABEL_FIELD = 'LABEL_FIELD'
    OUTPUT = 'OUTPUT'

    def tr(self, text: str) -> str:
        return text

    def displayName(self) -> str:
        return '求積表レイヤ生成'

    def name(self) -> str:
        return 'ksh_create_survey_table_layer'

    def group(self) -> str:
        return 'KSH'

    def groupId(self) -> str:
        return 'ksh'

    def shortHelpString(self) -> str:
        return '1行1頂点のテキスト表を出力し、属性テーブルアイテムで貼れるレイヤを生成する。'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT, '対象ポリゴン'))
        self.addParameter(QgsProcessingParameterString(self.LABEL_FIELD, '地物ラベル属性名', optional=True, defaultValue='地番'))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT, '出力レイヤ'))

    def processAlgorithm(self, parameters, context, feedback):
        raise QgsProcessingException('この環境では Processing アルゴリズムのロジックを実行できません。')
