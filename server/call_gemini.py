from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

def call_gemini(prompt):
    """調用 Google Gemini API 生成內容"""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("請設置 GEMINI_API_KEY 環境變數")
    else:
        client = genai.Client(
            api_key=api_key,
        )
        model = "gemini-2.5-flash-preview-04-17"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        system_prompt = '''
            你是一個專責「回饋文字處理」的語言模型助理
            你的處理流程固定為兩步：  
            1. 去識別化和語氣轉換 (固定為溫和)
            2. 主題分類

            ## 通用規則
            - 輸入為一段繁體中文原文 (string)。  
            - 所有輸出皆以 **單一 JSON 物件** 回傳，鍵順序固定：`deidentified_text` → `topics`。  
            - 禁止洩露任何個人可識別資訊 (PII)。  
            - 不可新增、刪減或重新排序鍵名；值中不得再嵌入 JSON。  

            ## 輸出格式
            ```json
            {
                "deidentified_text": "string",
                "topics": ["array", "of", "strings"],
            }
        '''
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=system_prompt),
            ],
        )

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

        return response.candidates[0].content.parts[0].text

print(call_gemini("請幫我寫一首關於春天的詩"))