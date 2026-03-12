"""
NLG Report Generator (Sim4Brief)
자연어 리포트 생성 서비스 - 3단계 상세도 지원
- brief: 핵심 요약 (1~2줄)
- detailed: 표준 리포트 (기본)
- comprehensive: 전체 분석 리포트 (경영진/학술용)
"""
from typing import Dict, Any, List, Literal
from loguru import logger

from app.core.config import settings
from app.models.schemas import NaturalLanguageReport


class NLGReportGenerator:
    """자연어 리포트 생성 (Sim4Brief 지원)"""

    @staticmethod
    def extract_formula(
        winner: Dict[str, Any],
        feature_names: List[str],
    ) -> str:
        """
        수학적 공식 생성

        Args:
            winner: 승자 알고리즘 결과
            feature_names: 특성 이름 리스트

        Returns:
            수학 공식 문자열
        """
        coefficients = winner.get("coefficients", {})

        if not coefficients:
            return f"{winner['algorithm_name']} 모델 (공식 추출 불가)"

        terms = []
        intercept = coefficients.get("intercept", 0)

        for feature in feature_names:
            coef = coefficients.get(feature, 0)
            if abs(coef) > 1e-6:
                sign = "+" if coef >= 0 else ""
                terms.append(f"{sign}{coef:.4f}*{feature}")

        formula = " ".join(terms)
        if intercept != 0:
            formula += f" + {intercept:.4f}"

        return f"Y = {formula}"

    @staticmethod
    def calculate_feature_importance(
        winner: Dict[str, Any],
        feature_names: List[str],
    ) -> Dict[str, float]:
        """
        변수 중요도 계산 (백분율)

        Args:
            winner: 승자 알고리즘 결과
            feature_names: 특성 이름 리스트

        Returns:
            {특성명: 중요도(%)} 딕셔너리
        """
        coefficients = winner.get("coefficients", {})

        if not coefficients:
            return {feature: 0.0 for feature in feature_names}

        abs_coefs = {
            feature: abs(coefficients.get(feature, 0))
            for feature in feature_names
        }

        total = sum(abs_coefs.values())
        if total == 0:
            return {feature: 0.0 for feature in feature_names}

        importance = {
            feature: (value / total) * 100
            for feature, value in abs_coefs.items()
        }

        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def generate_report(
        winner: Dict[str, Any],
        feature_importance: Dict[str, float],
        top_algorithms: List[Dict[str, Any]],
        task_type: str = "regression",
    ) -> NaturalLanguageReport:
        """
        자연어 리포트 생성

        Args:
            winner: 승자 알고리즘
            feature_importance: 변수 중요도
            top_algorithms: 상위 알고리즘 리스트
            task_type: 분석 유형

        Returns:
            자연어 리포트 객체
        """
        # 분석유형별 주요 지표 이름
        metric_name = NLGReportGenerator._get_primary_metric_name(task_type)
        metric_value = NLGReportGenerator._get_primary_metric_value(winner, task_type)

        # 요약
        summary = (
            f"총 {len(top_algorithms)}개 알고리즘 중 '{winner['algorithm_name']}'이(가) "
            f"최고 성능({metric_name}={metric_value:.4f})을 달성했습니다."
        )

        # 핵심 발견사항
        key_findings = [
            f"최적 모델: {winner['algorithm_name']}",
            f"{metric_name}: {metric_value:.4f} ({metric_value * 100:.2f}%)",
            f"실행 시간: {winner['execution_time']:.2f}초",
        ]

        if winner.get("adj_r2_score"):
            key_findings.append(f"조정된 R2: {winner['adj_r2_score']:.4f}")

        # 변수별 영향 설명
        variable_impacts = []
        for feature, importance in list(feature_importance.items())[:5]:
            coef = winner.get("coefficients", {}).get(feature, 0)
            direction = "증가" if coef > 0 else "감소"
            variable_impacts.append(
                f"'{feature}' 변수는 전체 영향력의 {importance:.2f}%를 차지하며, "
                f"값이 증가할 때 결과값을 {direction}시킵니다."
            )

        # 선정 사유
        selection_reason = (
            f"{winner['algorithm_name']}은(는) {len(top_algorithms)}개 후보 중 "
            f"가장 높은 {metric_name} 점수({metric_value:.4f})를 기록했습니다. "
        )

        if len(top_algorithms) > 1:
            second_best = top_algorithms[1]
            second_metric = NLGReportGenerator._get_primary_metric_value(second_best, task_type)
            gap = metric_value - second_metric
            selection_reason += (
                f"2위 알고리즘({second_best['algorithm_name']}, "
                f"{metric_name}={second_metric:.4f})보다 "
                f"{gap:.4f}만큼 우수한 성능을 보였습니다."
            )

        return NaturalLanguageReport(
            summary=summary,
            key_findings=key_findings,
            variable_impacts=variable_impacts,
            selection_reason=selection_reason,
        )

    @staticmethod
    def _get_primary_metric_name(task_type: str) -> str:
        """분석유형별 주요 지표명"""
        if task_type in ("classification", "multiclass"):
            return "F1"
        return "R2"

    @staticmethod
    def _get_primary_metric_value(result: Dict[str, Any], task_type: str) -> float:
        """분석유형별 주요 지표값"""
        if task_type in ("classification", "multiclass"):
            metrics = result.get("metrics", {})
            return metrics.get("f1_score", result.get("r2_score", 0.0))
        return result.get("r2_score", 0.0)

    # ─── Sim4Brief: 다단계 상세도 리포트 ─────────────

    @staticmethod
    def generate_sim4brief(
        winner: Dict[str, Any],
        feature_importance: Dict[str, float],
        top_algorithms: List[Dict[str, Any]],
        formula: str,
        task_type: str = "regression",
        detail_level: Literal["brief", "detailed", "comprehensive"] = "detailed",
    ) -> Dict[str, Any]:
        """
        Sim4Brief: 상세도 수준별 리포트 생성

        Args:
            winner: 승자 알고리즘 결과
            feature_importance: 변수 중요도
            top_algorithms: 상위 알고리즘 리스트
            formula: 수학 공식
            task_type: 분석 유형
            detail_level: 상세도 (brief/detailed/comprehensive)

        Returns:
            상세도별 리포트 딕셔너리
        """
        metric_name = NLGReportGenerator._get_primary_metric_name(task_type)
        metric_value = NLGReportGenerator._get_primary_metric_value(winner, task_type)

        if detail_level == "brief":
            return NLGReportGenerator._brief_report(
                winner, metric_name, metric_value, task_type
            )
        elif detail_level == "comprehensive":
            return NLGReportGenerator._comprehensive_report(
                winner, feature_importance, top_algorithms, formula,
                metric_name, metric_value, task_type,
            )
        else:
            # detailed (default)
            return NLGReportGenerator._detailed_report(
                winner, feature_importance, top_algorithms, formula,
                metric_name, metric_value, task_type,
            )

    @staticmethod
    def _brief_report(
        winner: Dict[str, Any],
        metric_name: str,
        metric_value: float,
        task_type: str,
    ) -> Dict[str, Any]:
        """Brief: 핵심 요약 1~2줄"""
        quality = "우수" if metric_value >= 0.85 else "양호" if metric_value >= 0.7 else "보통"

        return {
            "level": "brief",
            "summary": (
                f"'{winner['algorithm_name']}' 모델이 {metric_name}={metric_value:.4f}로 "
                f"선정되었습니다. ({quality})"
            ),
            "task_type": task_type,
            "metric": {metric_name: round(metric_value, 4)},
        }

    @staticmethod
    def _detailed_report(
        winner: Dict[str, Any],
        feature_importance: Dict[str, float],
        top_algorithms: List[Dict[str, Any]],
        formula: str,
        metric_name: str,
        metric_value: float,
        task_type: str,
    ) -> Dict[str, Any]:
        """Detailed: 표준 리포트"""
        # 핵심 발견
        findings = [
            f"최적 모델: {winner['algorithm_name']}",
            f"{metric_name}: {metric_value:.4f}",
        ]
        if winner.get("adj_r2_score"):
            findings.append(f"Adj R2: {winner['adj_r2_score']:.4f}")
        if winner.get("execution_time"):
            findings.append(f"실행 시간: {winner['execution_time']:.2f}초")

        # 상위 5개 변수
        top_vars = list(feature_importance.items())[:5]

        return {
            "level": "detailed",
            "summary": (
                f"총 {len(top_algorithms)}개 알고리즘 경쟁 결과, "
                f"'{winner['algorithm_name']}'이(가) {metric_name}={metric_value:.4f}로 "
                f"최적 모델로 선정되었습니다."
            ),
            "formula": formula,
            "findings": findings,
            "top_variables": [
                {"name": name, "importance_pct": round(imp, 2)} for name, imp in top_vars
            ],
            "task_type": task_type,
            "algorithms_tested": len(top_algorithms),
        }

    @staticmethod
    def _comprehensive_report(
        winner: Dict[str, Any],
        feature_importance: Dict[str, float],
        top_algorithms: List[Dict[str, Any]],
        formula: str,
        metric_name: str,
        metric_value: float,
        task_type: str,
    ) -> Dict[str, Any]:
        """Comprehensive: 경영진/학술용 전체 리포트"""
        # 모든 변수 영향도
        variable_analysis = []
        for name, imp in feature_importance.items():
            coef = winner.get("coefficients", {}).get(name, 0)
            direction = "양(+)" if coef > 0 else "음(-)" if coef < 0 else "무영향"
            variable_analysis.append({
                "name": name,
                "importance_pct": round(imp, 2),
                "coefficient": round(coef, 6),
                "direction": direction,
                "interpretation": (
                    f"'{name}' 변수가 1단위 증가할 때 결과값이 약 {abs(coef):.4f}만큼 "
                    f"{'증가' if coef > 0 else '감소'}합니다."
                    if abs(coef) > 1e-6
                    else f"'{name}' 변수는 결과에 유의미한 영향을 미치지 않습니다."
                ),
            })

        # 알고리즘 순위
        algo_ranking = []
        for i, algo in enumerate(top_algorithms[:10], 1):
            algo_metric = NLGReportGenerator._get_primary_metric_value(algo, task_type)
            algo_ranking.append({
                "rank": i,
                "name": algo["algorithm_name"],
                metric_name.lower(): round(algo_metric, 4),
                "execution_time": round(algo.get("execution_time", 0), 2),
            })

        # 모델 품질 평가
        quality_assessment = NLGReportGenerator._assess_model_quality(
            metric_value, task_type, len(top_algorithms)
        )

        return {
            "level": "comprehensive",
            "title": f"OmniMetric 분석 리포트 ({task_type.upper()})",
            "summary": (
                f"총 {len(top_algorithms)}개 알고리즘을 대상으로 한 토너먼트 결과, "
                f"'{winner['algorithm_name']}'이(가) {metric_name}={metric_value:.4f}로 "
                f"최적 모델로 선정되었습니다."
            ),
            "formula": formula,
            "quality_assessment": quality_assessment,
            "variable_analysis": variable_analysis,
            "algorithm_ranking": algo_ranking,
            "methodology": {
                "evaluation": "Train/Test Split (80:20) + Test 데이터 기반 평가",
                "metric": metric_name,
                "task_type": task_type,
                "total_candidates": len(top_algorithms),
            },
            "recommendations": NLGReportGenerator._generate_recommendations(
                metric_value, feature_importance, task_type
            ),
        }

    @staticmethod
    def _assess_model_quality(
        metric_value: float, task_type: str, n_algorithms: int
    ) -> Dict[str, Any]:
        """모델 품질 평가"""
        if metric_value >= 0.95:
            grade = "S"
            desc = "매우 우수 - 실무 적용 즉시 가능"
        elif metric_value >= 0.85:
            grade = "A"
            desc = "우수 - 높은 신뢰도로 의사결정 활용 가능"
        elif metric_value >= 0.70:
            grade = "B"
            desc = "양호 - 참고 자료로 활용 가능, 추가 데이터 확보 권장"
        elif metric_value >= 0.50:
            grade = "C"
            desc = "보통 - 추가 변수 탐색 또는 데이터 품질 개선 필요"
        else:
            grade = "D"
            desc = "미흡 - 모델 재설계 또는 데이터 근본적 재검토 필요"

        return {
            "grade": grade,
            "score": round(metric_value, 4),
            "description": desc,
            "algorithms_tested": n_algorithms,
        }

    @staticmethod
    def _generate_recommendations(
        metric_value: float,
        feature_importance: Dict[str, float],
        task_type: str,
    ) -> List[str]:
        """분석 결과 기반 권장사항 생성"""
        recs: List[str] = []

        if metric_value < 0.7:
            recs.append("모델 성능이 70% 미만입니다. 추가 변수 확보 또는 데이터 전처리 개선을 권장합니다.")
        if metric_value < 0.5:
            recs.append("분석 유형(regression/classification) 재검토를 권장합니다.")

        # 변수 집중도 체크
        top_importance = list(feature_importance.values())
        if top_importance and top_importance[0] > 80:
            recs.append(
                "단일 변수 의존도가 높습니다 (80%+). 다른 설명 변수 추가를 검토하세요."
            )

        if not recs:
            recs.append("분석 결과가 양호합니다. 정기적 모델 모니터링을 권장합니다.")

        return recs
