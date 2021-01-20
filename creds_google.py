import googleapiclient.discovery
from google.oauth2 import service_account


def G_Service(SERVICE_ACCOUNT_FILE, API_SERVICE_NAME, API_VERSION, *SCOPES):
    # 구글 API 연동
    GSCOPES = [scope for scope in SCOPES[0]]
    creds = None

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=GSCOPES)
        service = googleapiclient.discovery.build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=creds
        )
        print('"' + API_SERVICE_NAME + '"', '서비스 생성 성공')
        print('Parser Start!!')
        return service
    except Exception as e:
        print(e)
    return None
