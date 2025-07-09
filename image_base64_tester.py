import base64
import os
from PIL import Image
import io

def encode_image_to_base64(image_path):
    """
    이미지를 base64로 인코딩하는 함수
    
    Args:
        image_path (str): 이미지 파일 경로
        
    Returns:
        dict: 인코딩 결과와 메타데이터
    """
    try:
        # 이미지 파일 읽기
        with open(image_path, "rb") as image_file:
            # 원본 파일 크기 (KB)
            original_size_kb = os.path.getsize(image_path) / 1024
            
            # base64 인코딩
            image_data = image_file.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            # base64 인코딩된 문자열의 크기 (KB)
            base64_size_kb = len(base64_string.encode('utf-8')) / 1024
            
            # 이미지 MIME 타입 추출
            extension = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(extension, 'image/jpeg')
            
            return {
                'success': True,
                'base64_data': base64_string,
                'data_url': f"data:{mime_type};base64,{base64_string}",
                'original_size_kb': round(original_size_kb, 2),
                'encoded_size_kb': round(base64_size_kb, 2),
                'size_increase_percent': round((base64_size_kb/original_size_kb)*100, 1),
                'mime_type': mime_type,
                'base64_length': len(base64_string)
            }
            
    except FileNotFoundError:
        return {
            'success': False,
            'error': f"파일을 찾을 수 없습니다: {image_path}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"오류 발생: {str(e)}"
        }

def resize_image_to_target_size(image_path, target_size_kb):
    """
    이미지를 목표 크기(KB)에 맞게 리사이즈하고 base64로 인코딩
    
    Args:
        image_path (str): 이미지 파일 경로
        target_size_kb (float): 목표 크기 (KB)
        
    Returns:
        dict: 리사이즈 및 인코딩 결과
    """
    try:
        with Image.open(image_path) as img:
            # 이미지 형식 확인
            img_format = img.format if img.format else 'JPEG'
            
            # 원본 크기 저장
            original_width, original_height = img.size
            
            # 먼저 품질 조정으로 시도
            quality = 95
            while quality >= 10:
                buffer = io.BytesIO()
                img.save(buffer, format=img_format, quality=quality, optimize=True)
                buffer.seek(0)
                
                # base64 인코딩 및 크기 확인
                base64_string = base64.b64encode(buffer.read()).decode('utf-8')
                base64_size_kb = len(base64_string.encode('utf-8')) / 1024
                
                if base64_size_kb <= target_size_kb:
                    extension = '.' + img_format.lower()
                    mime_types = {
                        '.jpeg': 'image/jpeg',
                        '.jpg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.bmp': 'image/bmp',
                        '.webp': 'image/webp'
                    }
                    mime_type = mime_types.get(extension, 'image/jpeg')
                    
                    return {
                        'success': True,
                        'base64_data': base64_string,
                        'data_url': f"data:{mime_type};base64,{base64_string}",
                        'final_size_kb': round(base64_size_kb, 2),
                        'optimization_method': 'quality_adjustment',
                        'quality_used': quality,
                        'original_dimensions': f"{original_width}x{original_height}",
                        'final_dimensions': f"{original_width}x{original_height}",
                        'mime_type': mime_type
                    }
                
                quality -= 5
            
            # 품질 조정으로도 안 되면 크기 조정
            scale_factor = 0.95
            while scale_factor > 0.1:
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                
                # 이미지 리사이즈
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 다시 품질 조정 시도
                for quality in [85, 75, 65, 55, 45, 35, 25]:
                    buffer = io.BytesIO()
                    resized_img.save(buffer, format=img_format, quality=quality, optimize=True)
                    buffer.seek(0)
                    
                    base64_string = base64.b64encode(buffer.read()).decode('utf-8')
                    base64_size_kb = len(base64_string.encode('utf-8')) / 1024
                    
                    if base64_size_kb <= target_size_kb:
                        extension = '.' + img_format.lower()
                        mime_types = {
                            '.jpeg': 'image/jpeg',
                            '.jpg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif',
                            '.bmp': 'image/bmp',
                            '.webp': 'image/webp'
                        }
                        mime_type = mime_types.get(extension, 'image/jpeg')
                        
                        return {
                            'success': True,
                            'base64_data': base64_string,
                            'data_url': f"data:{mime_type};base64,{base64_string}",
                            'final_size_kb': round(base64_size_kb, 2),
                            'optimization_method': 'resize_and_quality',
                            'quality_used': quality,
                            'scale_factor': round(scale_factor, 2),
                            'original_dimensions': f"{original_width}x{original_height}",
                            'final_dimensions': f"{new_width}x{new_height}",
                            'mime_type': mime_type
                        }
                
                scale_factor -= 0.05
            
            return {
                'success': False,
                'error': f"목표 크기 {target_size_kb}KB로 줄일 수 없습니다."
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"이미지 리사이즈 중 오류: {str(e)}"
        }

def test_multiple_sizes(image_path, target_sizes):
    """
    여러 목표 크기로 테스트
    
    Args:
        image_path (str): 이미지 파일 경로
        target_sizes (list): 목표 크기들 (KB)
    """
    print(f"\n{'='*60}")
    print(f"이미지 파일: {image_path}")
    print(f"{'='*60}")
    
    # 원본 이미지 정보
    original_result = encode_image_to_base64(image_path)
    if original_result['success']:
        print(f"\n[원본 이미지 정보]")
        print(f"원본 파일 크기: {original_result['original_size_kb']} KB")
        print(f"Base64 인코딩 후 크기: {original_result['encoded_size_kb']} KB")
        print(f"크기 증가율: {original_result['size_increase_percent']}%")
        print(f"MIME 타입: {original_result['mime_type']}")
        print(f"Base64 문자열 길이: {original_result['base64_length']:,} 문자")
    else:
        print(f"오류: {original_result['error']}")
        return
    
    # 각 목표 크기별 테스트
    for target_size in target_sizes:
        print(f"\n[목표 크기: {target_size} KB]")
        result = resize_image_to_target_size(image_path, target_size)
        
        if result['success']:
            print(f"✅ 성공!")
            print(f"   최종 크기: {result['final_size_kb']} KB")
            print(f"   최적화 방법: {result['optimization_method']}")
            print(f"   품질: {result['quality_used']}")
            print(f"   원본 크기: {result['original_dimensions']}")
            print(f"   최종 크기: {result['final_dimensions']}")
            if 'scale_factor' in result:
                print(f"   크기 축소 비율: {result['scale_factor']}")
        else:
            print(f"❌ 실패: {result['error']}")

def create_json_response_example(image_path, target_size_kb=50):
    """
    Django JSON response 형태로 결과 출력
    
    Args:
        image_path (str): 이미지 파일 경로
        target_size_kb (float): 목표 크기 (KB)
    """
    print(f"\n{'='*60}")
    print(f"Django JSON Response 예시 (목표: {target_size_kb}KB)")
    print(f"{'='*60}")
    
    result = resize_image_to_target_size(image_path, target_size_kb)
    
    if result['success']:
        # Django에서 실제로 보낼 JSON 형태
        json_response = {
            'status': 'success',
            'image_data': result['base64_data'][:100] + '...',  # 너무 길어서 일부만 표시
            'image_info': {
                'size_kb': result['final_size_kb'],
                'mime_type': result['mime_type'],
                'dimensions': result['final_dimensions'],
                'optimization_method': result['optimization_method'],
                'quality': result['quality_used']
            },
            'data_url': result['data_url'][:150] + '...',  # 일부만 표시
        }
        
        print("JSON Response 구조:")
        import json
        print(json.dumps(json_response, indent=2, ensure_ascii=False))
        
        print(f"\n실제 base64 데이터 길이: {len(result['base64_data']):,} 문자")
        print(f"실제 data_url 길이: {len(result['data_url']):,} 문자")
        
    else:
        json_response = {
            'status': 'error',
            'message': result['error']
        }
        print("Error Response:")
        import json
        print(json.dumps(json_response, indent=2, ensure_ascii=False))

# 테스트 실행
if __name__ == "__main__":
    # 테스트할 이미지 파일 경로 (실제 파일로 변경하세요)
    test_image = "test_image.jpg"  # 여기에 실제 이미지 파일 경로를 입력하세요
    
    # 파일 존재 확인
    if not os.path.exists(test_image):
        print(f"❌ 테스트 이미지 파일이 없습니다: {test_image}")
        print("test_image 변수에 실제 이미지 파일 경로를 입력하세요.")
    else:
        # 1. 기본 인코딩 테스트
        print("🔍 기본 Base64 인코딩 테스트")
        basic_result = encode_image_to_base64(test_image)
        if basic_result['success']:
            print(f"✅ 성공!")
            print(f"   원본: {basic_result['original_size_kb']} KB")
            print(f"   인코딩 후: {basic_result['encoded_size_kb']} KB")
            print(f"   증가율: {basic_result['size_increase_percent']}%")
        
        # 2. 여러 크기로 리사이즈 테스트
        target_sizes = [10, 25, 50, 100, 200]
        test_multiple_sizes(test_image, target_sizes)
        
        # 3. Django JSON Response 예시
        create_json_response_example(test_image, 30)
