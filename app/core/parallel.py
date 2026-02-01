"""
Parallel Processing Engine with Ray
Ray 기반 분산 병렬 처리 시스템
"""
import ray
from typing import List, Dict, Any, Callable
from loguru import logger
import time

from app.core.config import settings


class RayCluster:
    """Ray 클러스터 관리"""

    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """Ray 클러스터 초기화"""
        if cls._initialized:
            logger.info("Ray 클러스터가 이미 초기화되어 있습니다.")
            return

        try:
            ray.init(
                address=settings.ray_address if settings.ray_address != "auto" else None,
                num_cpus=settings.ray_num_cpus,
                object_store_memory=settings.ray_object_store_memory,
                ignore_reinit_error=True,
                logging_level="INFO" if settings.is_development else "WARNING"
            )
            cls._initialized = True
            logger.info(
                f"✅ Ray 클러스터 초기화 완료 "
                f"(CPUs: {settings.ray_num_cpus}, "
                f"Memory: {settings.ray_object_store_memory / 1e9:.1f}GB)"
            )
        except Exception as e:
            logger.error(f"❌ Ray 클러스터 초기화 실패: {e}")
            raise

    @classmethod
    def shutdown(cls) -> None:
        """Ray 클러스터 종료"""
        if cls._initialized:
            ray.shutdown()
            cls._initialized = False
            logger.info("🛑 Ray 클러스터 종료 완료")

    @classmethod
    def is_initialized(cls) -> bool:
        """초기화 상태 확인"""
        return cls._initialized


@ray.remote
class AlgorithmWorker:
    """
    개별 알고리즘 실행 워커
    각 알고리즘을 독립적으로 실행하고 결과 반환
    """

    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        logger.info(f"워커 {worker_id} 초기화됨")

    def run_algorithm(
        self,
        algorithm_func: Callable,
        X: Any,
        y: Any,
        algorithm_name: str
    ) -> Dict[str, Any]:
        """
        알고리즘 실행

        Args:
            algorithm_func: 실행할 알고리즘 함수
            X: 독립 변수
            y: 종속 변수
            algorithm_name: 알고리즘 이름

        Returns:
            실행 결과 딕셔너리 (r2_score, execution_time 등)
        """
        start_time = time.time()
        logger.info(f"워커 {self.worker_id}: {algorithm_name} 실행 시작")

        try:
            result = algorithm_func(X, y)
            execution_time = time.time() - start_time

            logger.info(
                f"워커 {self.worker_id}: {algorithm_name} 완료 "
                f"(R²={result.get('r2_score', 0):.4f}, {execution_time:.2f}초)"
            )

            return {
                "algorithm_name": algorithm_name,
                "r2_score": result.get("r2_score", 0.0),
                "adj_r2_score": result.get("adj_r2_score"),
                "p_value": result.get("p_value"),
                "execution_time": execution_time,
                "model": result.get("model"),
                "coefficients": result.get("coefficients", {}),
                "status": "success",
                "error": None
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"워커 {self.worker_id}: {algorithm_name} 실패 - {str(e)}")

            return {
                "algorithm_name": algorithm_name,
                "r2_score": -1.0,
                "adj_r2_score": None,
                "p_value": None,
                "execution_time": execution_time,
                "model": None,
                "coefficients": {},
                "status": "failed",
                "error": str(e)
            }


class ParallelTournament:
    """
    병렬 알고리즘 토너먼트 관리자
    60개 알고리즘을 동시에 실행하고 결과 집계
    """

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or settings.tournament_max_workers

        if not RayCluster.is_initialized():
            RayCluster.initialize()

    def run_tournament(
        self,
        algorithms: List[tuple[str, Callable]],
        X: Any,
        y: Any
    ) -> List[Dict[str, Any]]:
        """
        병렬 토너먼트 실행

        Args:
            algorithms: (알고리즘_이름, 알고리즘_함수) 튜플 리스트
            X: 독립 변수
            y: 종속 변수

        Returns:
            모든 알고리즘 실행 결과 리스트
        """
        logger.info(f"🏁 토너먼트 시작: {len(algorithms)}개 알고리즘")
        start_time = time.time()

        # Ray 객체 저장소에 데이터 업로드 (한 번만)
        X_ref = ray.put(X)
        y_ref = ray.put(y)

        # 워커 풀 생성
        workers = [AlgorithmWorker.remote(i) for i in range(self.max_workers)]
        logger.info(f"워커 풀 생성 완료: {len(workers)}개 워커")

        # 작업 분배 및 실행
        futures = []
        for idx, (algo_name, algo_func) in enumerate(algorithms):
            worker = workers[idx % len(workers)]  # 라운드 로빈 할당
            future = worker.run_algorithm.remote(
                algo_func,
                X_ref,
                y_ref,
                algo_name
            )
            futures.append(future)

        # 모든 작업 완료 대기
        logger.info(f"모든 워커에게 작업 할당 완료. 결과 수집 중...")
        results = ray.get(futures)

        total_time = time.time() - start_time
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "failed"]

        logger.info(
            f"🏆 토너먼트 완료: "
            f"{len(successful)}개 성공, {len(failed)}개 실패 "
            f"(총 소요 시간: {total_time:.2f}초)"
        )

        return results

    def get_top_performers(
        self,
        results: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        상위 N개 알고리즘 추출

        Args:
            results: 토너먼트 결과 리스트
            top_n: 추출할 개수

        Returns:
            상위 N개 알고리즘 결과
        """
        # 성공한 알고리즘만 필터링
        successful = [r for r in results if r["status"] == "success" and r["r2_score"] >= 0]

        # R² 점수 기준 내림차순 정렬
        sorted_results = sorted(
            successful,
            key=lambda x: x["r2_score"],
            reverse=True
        )

        top_performers = sorted_results[:top_n]

        logger.info(f"🥇 상위 {top_n}개 알고리즘:")
        for idx, result in enumerate(top_performers, 1):
            logger.info(
                f"  {idx}. {result['algorithm_name']}: "
                f"R²={result['r2_score']:.4f} "
                f"({result['execution_time']:.2f}초)"
            )

        return top_performers

    def get_winner(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        최고 성능 알고리즘 선정

        Args:
            results: 토너먼트 결과 리스트

        Returns:
            승자 알고리즘 결과
        """
        top_performers = self.get_top_performers(results, top_n=1)

        if not top_performers:
            raise ValueError("성공한 알고리즘이 없습니다.")

        winner = top_performers[0]
        logger.info(
            f"👑 승자: {winner['algorithm_name']} "
            f"(R²={winner['r2_score']:.4f})"
        )

        return winner
