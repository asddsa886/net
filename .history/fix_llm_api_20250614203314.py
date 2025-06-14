# 临时修复脚本，用于修复 llm_composer.py 中的 API 调用错误

import re

def fix_llm_composer():
    """修复 llm_composer.py 中的 API 调用错误"""
    
    # 读取文件
    with open('src/llm_composer.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复错误的 API 调用代码
    old_code = '''            response = requests.post(
                f'{self.base_url}',
                headers=headers,
                json=data,
                timeout=30
            )

            # 输出result
            print(f"API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

            
            if response.status_code == 200:
                result = response.json()
                
                return result['choices'][0]['message']['content']
            else:
                print(f"API调用失败: {response.status_code}")
                return self._simulate_llm_response(prompt)'''
    
    new_code = '''            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"API调用成功，返回 {len(result.get('choices', []))} 个选择")
                return result['choices'][0]['message']['content']
            else:
                print(f"API调用失败: {response.status_code}")
                if response.text:
                    print(f"错误详情: {response.text[:200]}...")
                return self._simulate_llm_response(prompt)'''
    
    # 替换内容
    content = content.replace(old_code, new_code)
    
    # 写回文件
    with open('src/llm_composer.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已修复 llm_composer.py 中的 API 调用错误")
    print("主要修复:")
    print("1. 移除了未定义的 result 变量打印")
    print("2. 修正了 API 端点路径")
    print("3. 改进了错误处理")

if __name__ == "__main__":
    fix_llm_composer()
