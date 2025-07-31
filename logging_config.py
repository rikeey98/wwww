# logging_config.py
import logging
import logging.handlers
import os
import json
from datetime import datetime
from functools import wraps
import streamlit as st
import time
import traceback
import psutil


class StreamlitLogger:
    """Streamlit 애플리케이션용 통합 로깅 시스템"""
    
    def __init__(self, log_dir="/var/log/streamlit-app", app_name="streamlit-app"):
        self.log_dir = log_dir
        self.app_name = app_name
        self.loggers = {}
        
        # 로그 디렉토리 생성
        os.makedirs(log_dir, exist_ok=True)
        
        # 각종 로거 초기화
        self._setup_loggers()
    
    def _setup_loggers(self):
        """모든 로거를 설정합니다"""
        
        # 1. 애플리케이션 로거 (일반적인 앱 동작)
        self.loggers['app'] = self._create_logger(
            name='app',
            filename='app.log',
            level=logging.INFO,
            format_type='detailed'
        )
        
        # 2. 접근 로거 (사용자 요청/접근)
        self.loggers['access'] = self._create_logger(
            name='access',
            filename='access.log',
            level=logging.INFO,
            format_type='access'
        )
        
        # 3. 에러 로거 (에러 전용)
        self.loggers['error'] = self._create_logger(
            name='error',
            filename='error.log',
            level=logging.ERROR,
            format_type='error'
        )
        
        # 4. 디버그 로거 (개발/디버깅)
        self.loggers['debug'] = self._create_logger(
            name='debug',
            filename='debug.log',
            level=logging.DEBUG,
            format_type='debug'
        )
        
        # 5. 성능 로거 (성능 모니터링)
        self.loggers['performance'] = self._create_logger(
            name='performance',
            filename='performance.log',
            level=logging.INFO,
            format_type='performance'
        )
    
    def _create_logger(self, name, filename, level, format_type):
        """개별 로거를 생성합니다"""
        logger = logging.getLogger(f"{self.app_name}_{name}")
        logger.setLevel(level)
        
        # 기존 핸들러 제거 (중복 방지)
        logger.handlers.clear()
        
        # 로테이팅 파일 핸들러
        file_path = os.path.join(self.log_dir, filename)
        handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=100*1024*1024,  # 100MB
            backupCount=30,  # 30개 파일 보관
            encoding='utf-8'
        )
        
        # 포맷터 설정
        formatter = self._get_formatter(format_type)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False  # 상위 로거로 전파 방지
        
        return logger
    
    def _get_formatter(self, format_type):
        """포맷 타입별 포맷터를 반환합니다"""
        formats = {
            'detailed': '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            'access': '%(asctime)s | ACCESS | %(message)s',
            'error': '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s | %(exc_info)s',
            'debug': '%(asctime)s | DEBUG | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            'performance': '%(asctime)s | PERF | %(message)s'
        }
        
        return logging.Formatter(
            formats.get(format_type, formats['detailed']),
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # === 편의 메소드들 ===
    
    def info(self, message, **kwargs):
        """일반 정보 로그"""
        extra_info = self._format_extra_info(**kwargs)
        self.loggers['app'].info(f"{message} {extra_info}")
    
    def warning(self, message, **kwargs):
        """경고 로그"""
        extra_info = self._format_extra_info(**kwargs)
        self.loggers['app'].warning(f"{message} {extra_info}")
    
    def error(self, message, exception=None, **kwargs):
        """에러 로그"""
        extra_info = self._format_extra_info(**kwargs)
        error_msg = f"{message} {extra_info}"
        
        if exception:
            error_msg += f" | Exception: {str(exception)}"
            self.loggers['error'].error(error_msg, exc_info=True)
        else:
            self.loggers['error'].error(error_msg)
    
    def debug(self, message, **kwargs):
        """디버그 로그"""
        extra_info = self._format_extra_info(**kwargs)
        self.loggers['debug'].debug(f"{message} {extra_info}")
    
    def access_log(self, user_id, session_id, action, page=None, **kwargs):
        """사용자 접근 로그"""
        access_info = {
            'user_id': user_id,
            'session_id': session_id,
            'action': action,
            'page': page,
            **kwargs
        }
        self.loggers['access'].info(json.dumps(access_info, ensure_ascii=False))
    
    def performance_log(self, operation, duration, **kwargs):
        """성능 로그"""
        perf_info = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        self.loggers['performance'].info(json.dumps(perf_info, ensure_ascii=False))
    
    def _format_extra_info(self, **kwargs):
        """추가 정보를 포맷팅합니다"""
        if not kwargs:
            return ""
        return "| " + " | ".join([f"{k}={v}" for k, v in kwargs.items()])


class LoggingDecorators:
    """로깅 데코레이터 모음"""
    
    def __init__(self, logger: StreamlitLogger):
        self.logger = logger
    
    def log_execution_time(self, operation_name=None):
        """함수 실행 시간을 로깅하는 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                operation = operation_name or func.__name__
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.logger.performance_log(
                        operation=operation,
                        duration=duration,
                        status='success'
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.logger.performance_log(
                        operation=operation,
                        duration=duration,
                        status='error',
                        error=str(e)
                    )
                    raise
            return wrapper
        return decorator
    
    def log_user_action(self, action_name=None):
        """사용자 액션을 로깅하는 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                action = action_name or func.__name__
                user_id = self._get_user_id()
                session_id = self._get_session_id()
                
                self.logger.access_log(
                    user_id=user_id,
                    session_id=session_id,
                    action=action
                )
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def log_errors(self, reraise=True):
        """에러를 자동으로 로깅하는 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(
                        f"Error in {func.__name__}",
                        exception=e,
                        function=func.__name__,
                        args=str(args)[:200],  # 너무 길면 자름
                        kwargs=str(kwargs)[:200]
                    )
                    if reraise:
                        raise
                    return None
            return wrapper
        return decorator
    
    def _get_user_id(self):
        """현재 사용자 ID 추출 (세션 상태에서)"""
        return getattr(st.session_state, 'user_id', 'anonymous')
    
    def _get_session_id(self):
        """현재 세션 ID 추출"""
        return getattr(st.session_state, 'session_id', 'unknown')


class SystemMonitor:
    """시스템 리소스 모니터링"""
    
    def __init__(self, logger: StreamlitLogger):
        self.logger = logger
    
    def log_system_stats(self):
        """시스템 통계를 로깅합니다"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            
            system_stats = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2)
            }
            
            self.logger.performance_log(
                operation='system_monitor',
                duration=0,
                **system_stats
            )
            
        except Exception as e:
            self.logger.error("Failed to collect system stats", exception=e)


# === 사용 예시 ===

# 전역 로거 인스턴스 생성
logger = StreamlitLogger()
decorators = LoggingDecorators(logger)
monitor = SystemMonitor(logger)

def setup_logging():
    """로깅 시스템 초기화"""
    # 세션 ID 생성 (한 번만)
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    # 사용자 ID 설정 (로그인 시스템이 있다면)
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "anonymous"
    
    # 앱 시작 로그
    logger.access_log(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
        action="app_start",
        page="main"
    )

@decorators.log_execution_time("data_processing")
@decorators.log_user_action("process_data")
@decorators.log_errors()
def process_data(data):
    """데이터 처리 함수 예시"""
    logger.info("Starting data processing", data_size=len(data))
    
    # 복잡한 처리 로직
    time.sleep(1)  # 시뮬레이션
    
    result = len(data) * 2
    logger.info("Data processing completed", result=result)
    return result

def main():
    """메인 애플리케이션"""
    st.title("Streamlit with Professional Logging")
    
    # 로깅 시스템 초기화
    setup_logging()
    
    # 시스템 모니터링 (주기적으로)
    if st.button("System Status"):
        monitor.log_system_stats()
        st.success("System stats logged!")
    
    # 사용자 액션 테스트
    if st.button("Process Data"):
        try:
            test_data = list(range(100))
            result = process_data(test_data)
            st.success(f"Processing completed! Result: {result}")
            
        except Exception as e:
            st.error("Processing failed!")
            logger.error("Data processing failed", exception=e)
    
    # 에러 테스트
    if st.button("Trigger Error"):
        try:
            raise ValueError("This is a test error")
        except Exception as e:
            logger.error("Test error occurred", exception=e)
            st.error("Error logged successfully!")
    
    # 로그 정보 표시
    st.subheader("Logging Info")
    st.write(f"Session ID: {st.session_state.get('session_id', 'Not set')}")
    st.write(f"User ID: {st.session_state.get('user_id', 'Not set')}")
    st.write(f"Log Directory: {logger.log_dir}")

if __name__ == "__main__":
    main()
