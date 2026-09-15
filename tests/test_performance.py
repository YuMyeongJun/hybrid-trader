"""Performance and speed tests for Hybrid Trader.

This module tests the performance characteristics of the trading engine,
including API response times, memory usage, and throughput.

성능 및 속도 테스트를 수행합니다.
"""

import pytest
import time
import psutil
import os
from unittest.mock import Mock, patch, MagicMock
from hybrid_trader.engine import HybridTradingEngine
from hybrid_trader.config import TradingConfig


@pytest.mark.performance
class TestPerformanceEngine:
    """Test performance characteristics of HybridTradingEngine."""

    def test_engine_initialization_time(self, trading_config):
        """Test that engine initialization is fast (<100ms).

        엔진 초기화 속도 테스트 (<100ms)
        """
        start = time.perf_counter()
        engine = HybridTradingEngine(trading_config)
        elapsed = time.perf_counter() - start

        # Should initialize quickly
        assert elapsed < 0.1, f"Engine init took {elapsed:.3f}s, expected < 0.1s"

    def test_multiple_engine_instances_creation(self, trading_config):
        """Test creating multiple engine instances performance.

        여러 엔진 인스턴스 생성 성능 테스트
        """
        num_engines = 100
        start = time.perf_counter()

        engines = [HybridTradingEngine(trading_config) for _ in range(num_engines)]

        elapsed = time.perf_counter() - start
        avg_time = elapsed / num_engines

        assert avg_time < 0.01, f"Average creation took {avg_time:.4f}s"
        assert len(engines) == num_engines

    def test_memory_usage_during_operations(self, trading_engine):
        """Test memory usage doesn't grow unbounded during operations.

        작업 중 메모리 사용량 테스트
        """
        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate some operations (mocked to be fast)
        with patch.object(trading_engine, 'get_stock_price', return_value=50000):
            for _ in range(1000):
                trading_engine.get_stock_price("005930")

        # Check memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory

        # Memory increase should be reasonable (< 50MB for 1000 calls)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"

    @pytest.mark.slow
    def test_concurrent_operations_performance(self, trading_engine):
        """Test performance under concurrent operations.

        동시 작업 성능 테스트
        """
        import concurrent.futures

        def mock_operation():
            with patch.object(trading_engine, 'get_stock_price', return_value=50000):
                return trading_engine.get_stock_price("005930")

        num_threads = 10
        operations_per_thread = 100

        start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(mock_operation)
                for _ in range(num_threads * operations_per_thread)
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        elapsed = time.perf_counter() - start
        total_operations = num_threads * operations_per_thread
        ops_per_second = total_operations / elapsed

        # Should handle at least 100 ops/second
        assert ops_per_second > 100, f"Only {ops_per_second:.0f} ops/sec"
        assert len(results) == total_operations


@pytest.mark.performance
class TestAPIResponseTime:
    """Test API response time performance."""

    def test_stock_price_query_time(self, trading_engine):
        """Test stock price query response time (<500ms).

        주식 가격 조회 응답 시간 테스트
        """
        with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
            start = time.perf_counter()
            result = trading_engine.get_stock_price("005930")
            elapsed = time.perf_counter() - start

        assert result is not None
        # Mocked API should be very fast, but allow reasonable margin
        assert elapsed < 0.5, f"Query took {elapsed:.3f}s"

    def test_coin_price_query_time(self, trading_engine):
        """Test coin price query response time (<500ms).

        암호화폐 가격 조회 응답 시간 테스트
        """
        mock_response = {"trade_price": 50000000}
        with patch.object(trading_engine.upbit_session, 'get_ticker', return_value=mock_response):
            start = time.perf_counter()
            result = trading_engine.get_coin_price("KRW-BTC")
            elapsed = time.perf_counter() - start

        assert result is not None
        assert elapsed < 0.5, f"Query took {elapsed:.3f}s"

    def test_batch_queries_throughput(self, trading_engine):
        """Test throughput of batch queries.

        배치 조회 처리량 테스트
        """
        tickers = ["005930", "000660", "005380", "051910", "207940"]

        with patch.object(trading_engine.kis_session, 'get_price', return_value=50000):
            start = time.perf_counter()
            results = [trading_engine.get_stock_price(ticker) for ticker in tickers]
            elapsed = time.perf_counter() - start

        assert len(results) == len(tickers)
        assert all(r is not None for r in results)

        # Should handle 5 queries in < 1 second
        assert elapsed < 1.0, f"Batch took {elapsed:.3f}s"


@pytest.mark.performance
class TestMemoryOptimization:
    """Test memory optimization and efficiency."""

    def test_session_lazy_loading_memory(self, trading_config):
        """Test that lazy loading doesn't pre-allocate unnecessary memory.

        지연 로딩으로 불필요한 메모리 미리 할당 방지 테스트
        """
        process = psutil.Process(os.getpid())
        baseline = process.memory_info().rss / 1024 / 1024

        engine = HybridTradingEngine(trading_config)

        after_init = process.memory_info().rss / 1024 / 1024
        increase = after_init - baseline

        # Creating engine should not use significant memory
        assert increase < 10, f"Engine init used {increase:.2f}MB"

    def test_large_dataset_processing(self, trading_engine):
        """Test memory efficiency with large datasets.

        대량 데이터 처리 메모리 효율성 테스트
        """
        process = psutil.Process(os.getpid())
        baseline = process.memory_info().rss / 1024 / 1024

        # Simulate processing many records
        large_list = list(range(1000000))  # 1M integers

        after_creation = process.memory_info().rss / 1024 / 1024
        increase = after_creation - baseline

        # Should be reasonable (rough estimate for 1M integers)
        assert increase < 100, f"Large list used {increase:.2f}MB"

        # Clean up
        del large_list


@pytest.mark.performance
class TestStartupAndShutdown:
    """Test startup and shutdown performance."""

    def test_engine_startup_time_with_context_manager(self, trading_config):
        """Test context manager startup time.

        Context Manager 시작 시간 테스트
        """
        start = time.perf_counter()
        with HybridTradingEngine(trading_config) as engine:
            elapsed_init = time.perf_counter() - start
            assert engine is not None

        assert elapsed_init < 0.2, f"Context manager init took {elapsed_init:.3f}s"

    def test_bulk_operation_with_retry_overhead(self, trading_engine):
        """Test performance impact of retry logic.

        재시도 로직의 성능 영향 테스트
        """
        # Simulate operation with potential retries
        call_count = 0

        def mock_with_retries(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return 50000

        with patch.object(trading_engine.kis_session, 'get_price', side_effect=mock_with_retries):
            start = time.perf_counter()
            result = trading_engine.get_stock_price("005930")
            elapsed = time.perf_counter() - start

        assert result == 50000
        assert elapsed < 0.1, f"Operation took {elapsed:.3f}s"
