# lambda/index.py
import json
import os
import urllib.request
import urllib.error
import re  # 正規表現モジュールをインポート
from botocore.exceptions import ClientError

# 環境変数からAPIのURLを取得する（デフォルトはダミーURL）
FASTAPI_ENDPOINT = "https://19cd-34-106-214-35.ngrok-free.app/chat"

# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値

# グローバル変数としてクライアントを初期化（初期値）
bedrock_client = None

# モデルID
MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディをパース
        body = json.loads(event['body'])
        message = body['message']
        
        print("Processing message:", message)
        
        # FastAPIに送るためのデータを作成
        request_data = {
            "message": message
        }
        request_body = json.dumps(request_data).encode('utf-8')
        
        # FastAPIエンドポイントにリクエストを送信
        req = urllib.request.Request(
            FASTAPI_ENDPOINT,
            data=request_body,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            response_body = response.read()
            response_data = json.loads(response_body)
        
        print("FastAPI response:", json.dumps(response_data))
        
        # FastAPI側の応答から必要な情報を取り出す
        assistant_response = response_data.get('response', 'No response')
        
        # 成功レスポンスを返す
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
