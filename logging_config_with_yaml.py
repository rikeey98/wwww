# logging_config.py - YAML 설정 파일을 사용하는 버전
import logging
import logging.handlers
import os
import json
import yaml
from datetime import datetime
from functools import wraps
import streamlit as st
import time
import traceback
import psutil
from pathlib import Path


class ConfigManager:
    """YAML 설정 파일 관리자"""
    
    def __init__(self, config_file="logging_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """YAML 설정 파일 로드"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                print(f"✅ 설정 파일 로드 성공: {self.config_file}")
                return config
            else:
                print(f"⚠️ 설정 파일 없음: {self.config_file}, 기본 설정 사용")
                return self._get_default_config()
        except Exception as e:
            print(f"❌ 설정 파일 로드 실패: {e}, 기본 설정 사용")
            return self._get_default_config()
    
    def _get_default_config(self):
        """기본 설정 반환"""
        return {
            'default': {
                'log_dir': './logs',
                'app_name': 'streamlit-app',
                'encoding': 'utf-8'
            },
            'environments': {
                'development': {
                    'log_level': 'DEBUG',
                    'console_output': True,
                    'file_rotation': {
                        'max_bytes': 50_000_000,
                        'backup_count': 10
                    }
                }
            },
            'loggers': {
                'app': {'filename': 'app.log', 'level': 'INFO', 'format': 'detailed'},
                'access': {'filename': 'access.log', 'level': 'INFO', 'format': 'access'},
                'error': {'filename': 'error.log', 'level': 'ERROR', 'format': 'error'},
                'debug': {'filename': 'debug.log', 'level': 'DEBUG', 'format': 'debug'},
                'performance': {'filename': 'performance.log', 'level': 'INFO', 'format': 'performance'}
            },
            'formats': {
                'detailed': '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                'access': '%(asctime)s | ACCESS | %(message)s',
                'error': '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                'debug': '%(asctime)s | DEBUG | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                'performance': '%(asctime)s | PERF | %(message)s'
            }
        }
    
    def get(self, key_path, default=None):
        """점 표기법으로 설정값 가져오기 (예: 'default.log_dir')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_environment(self):
        """현재 환경 감지 (개발/운영)"""
        # 환경 변수나 다른 방법으로 환경 감지 가능
        env = os.getenv('STREAMLIT_ENV', 'development')
        return env if env in ['development', 'production'] else 'development'


class StreamlitLogger:
    """Streamlit 애플리케이션용 통합 로깅 시스템 - YAML 설정 사용"""
    
    def __init__(self, config_file="logging_config.yaml"):
        self.config_manager = ConfigManager(config_file)
        self.environment = self.config_manager.get_environment()
        
        # 설정값 로드
        self.log_dir = self.config_manager.get('default.log_dir', './logs')
        self.app_name = self.config_manager.get('default.app_name', 'streamlit-app')
        self.encoding = self.config_manager.get('default.encoding', 'utf-8')
        
        # 환경별 설정
        env_config = self.config_manager.get(f'environments.{self.environment}', {})
        self.max_bytes = env_config.get('file_rotation', {}).get('max_bytes', 100_000_000)
        self.backup_count = env_config.get('file_rotation', {}).get('backup_count', 30)
        self.console_output = env_config.get('console_output', False)
        
        self.loggers = {}
        
        # 로그 디렉토리 생성
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 설정 정보 출력
        self._print_config_info()
        
        # 각종 로거 초기화
        self._setup_loggers()
    
    def _print_config_info(self):
        """현재 설정 정보 출력"""
        print(f"🔧 로깅 설정 정보:")
        print(f"   환경: {self.environment}")
        print(f"   로그 디렉토리: {self.log_dir}")
        print(f"   앱 이름: {self.app_name}")
        print(f"   파일 최대 크기: {self.max_bytes // (1024*1024)}MB")
        print(f"   백업 파일 수: {self.backup_count}")
        print(f"   콘솔 출력: {self.console_output}")
    
    def _setup_loggers(self):
        """YAML 설정을 기반으로 모든 로거를 설정합니다"""
        
        logger_configs = self.config_manager.get('loggers', {})
        
        for logger_name, logger_config in logger_configs.items():
            self.loggers[logger_name] = self._create_logger(
                name=logger_name,
                filename=logger_config.get('filename', f'{logger_name}.log'),
                level=getattr(logging, logger_config.get('level', 'INFO')),
                format_type=logger_config.get('format', 'detailed')
            )
        
        print(f"✅ {len(self.loggers)}개 로거 초기화 완료: {list(self.loggers.keys())}")
    
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
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding=self.encoding
        )
        
        # 포맷터 설정
        formatter = self._get_formatter(format_type)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # 콘솔 출력 (개발 환경에서만)
        if self.console_output and self.environment == 'development':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        logger.propagate = False  # 상위 로거로 전파 방지
        
        return logger
    
    def _get_formatter(self, format_type):
        """포맷 타입별 포맷터를 반환합니다"""
        formats = self.config_manager.get('formats', {})
        format_string = formats.get(format_type, formats.get('detailed', 
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'))
        
        return logging.Formatter(
            format_string,
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
            'environment': self.environment,
            **kwargs
        }
        self.loggers['performance'].info(json.dumps(perf_info, ensure_ascii=False))
    
    def _format_extra_info(self, **kwargs):
        """추가 정보를 포맷팅합니다"""
        if not kwargs:
            return ""
        return "| " + " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    
    def get_config_info(self):
        """현재 설정 정보를 딕셔너리로 반환"""
        return {
            'environment': self.environment,
            'log_dir': self.log_dir,
            'app_name': self.app_name,
            'max_bytes_mb': self.max_bytes // (1024*1024),
            'backup_count': self.backup_count,
            'console_output': self.console_output,
            'loggers': list(self.loggers.keys())
        }


class LoggingDecorators:
    """로깅 데코레이터 모음 - 설정 인식"""
    
    def __init__(self, logger: StreamlitLogger):
        self.logger = logger
        self.config_manager = logger.config_manager
        
        # 성능 임계값 설정에서 가져오기
        self.performance_threshold_ms = self.config_manager.get(
            'monitoring.performance_threshold_ms', 5000
        )
    
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
                    
                    # 성능 임계값 체크
                    if duration * 1000 > self.performance_threshold_ms:
                        self.logger.warning(
                            f"Slow operation detected: {operation}",
                            duration_ms=round(duration * 1000, 2),
                            threshold_ms=self.performance_threshold_ms
                        )
                    
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
    """시스템 리소스 모니터링 - 설정 기반"""
    
    def __init__(self, logger: StreamlitLogger):
        self.logger = logger
        self.config_manager = logger.config_manager
        self.monitoring_enabled = self.config_manager.get('monitoring.system_stats', True)
    
    def log_system_stats(self):
        """시스템 통계를 로깅합니다"""
        if not self.monitoring_enabled:
            self.logger.debug("시스템 모니터링이 비활성화됨")
            return
        
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


# === 설정 기반 초기화 ===

def create_logger_with_config(config_file="logging_config.yaml"):
    """설정 파일을 기반으로 로거 시스템 생성"""
    logger = StreamlitLogger(config_file)
    decorators = LoggingDecorators(logger)
    monitor = SystemMonitor(logger)
    
    return logger, decorators, monitor
