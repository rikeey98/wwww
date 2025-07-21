이슈 키로 transition 정보를 가져오는 함수를 만들어드리겠습니다.
기본 이슈 Transition 정보 조회 함수
pythondef get_issue_transitions(jira, issue_key):
    """
    특정 이슈의 사용 가능한 transition 정보를 조회하는 함수
    
    Args:
        jira: Jira 인스턴스
        issue_key: 이슈 키 (예: 'TEST-123')
    
    Returns:
        dict: transition 정보
    """
    try:
        # 이슈의 현재 상태와 사용 가능한 transitions 조회
        transitions_response = jira.get(f'rest/api/3/issue/{issue_key}/transitions')
        
        # 현재 이슈 정보도 함께 조회
        issue_info = jira.get(f'rest/api/3/issue/{issue_key}', params={'fields': 'status'})
        current_status = issue_info['fields']['status']['name']
        
        transitions = []
        for trans in transitions_response.get('transitions', []):
            transitions.append({
                'id': trans['id'],
                'name': trans['name'],
                'to_status': trans['to']['name'],
                'to_status_id': trans['to']['id']
            })
        
        return {
            'success': True,
            'issue_key': issue_key,
            'current_status': current_status,
            'available_transitions': transitions,
            'transition_count': len(transitions)
        }
        
    except Exception as e:
        return {
            'success': False,
            'issue_key': issue_key,
            'error': str(e)
        }

# 사용 예시
transitions = get_issue_transitions(jira, 'TEST-123')

if transitions['success']:
    print(f"Issue: {transitions['issue_key']}")
    print(f"Current Status: {transitions['current_status']}")
    print(f"Available Transitions ({transitions['transition_count']}):")
    
    for trans in transitions['available_transitions']:
        print(f"  - {trans['name']} (ID: {trans['id']}) -> {trans['to_status']}")
