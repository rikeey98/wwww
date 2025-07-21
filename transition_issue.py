def transition_issue(jira, issue_key, transition_id):
    """
    이슈 상태를 간단하게 변경하는 함수
    
    Args:
        jira: Jira 인스턴스
        issue_key: 이슈 키 (예: 'TEST-123')
        transition_id: 전환 ID (숫자 또는 문자열)
    
    Returns:
        bool: 성공 시 True, 실패 시 False
    """
    try:
        jira.post(
            f'rest/api/3/issue/{issue_key}/transitions',
            data={
                "transition": {
                    "id": str(transition_id)
                }
            }
        )
        return True
    except:
        return False

# 사용 예시
success = transition_issue(jira, 'TEST-123', '21')
print(f"Transition success: {success}")
