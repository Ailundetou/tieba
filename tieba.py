import json
import sys
import requests # 必须导入
from types import SimpleNamespace

# 1. 加载配置
try:
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
except FileNotFoundError:
    print("错误：找不到 data.json 文件")
    sys.exit(1)

# 全局 Headers
headers = {
    "Authorization": data.TOKEN,
    "Content-Type": "application/json"
}

def create_thread(title, content):
    payload = {
        "title": title,
        "content": [{"type": "text", "content": content}],
        "tab_id": 0
    }
    try:
        response = requests.post(data.create_thread_URL, json=payload, headers=headers)
        res_data = response.json()
        if res_data.get("errno") == 0:
            tid = res_data.get("data", {}).get("thread_id")
            print(f"✅ 发帖成功！链接: https://tieba.baidu.com/p/{tid}")
        else:
            print(f"❌ 失败: {res_data.get('errmsg')}")
    except Exception as e:
        print(f"⚠️ 网络出错: {e}")

def check_reply():
    try:
        # GET 请求建议不带 Content-Type，直接用 headers 字典的 copy
        get_headers = {"Authorization": data.TOKEN}
        response = requests.get(data.check_reply_URL, headers=get_headers)
        res_data = response.json()

        if res_data.get("no") == 0:
            replies = res_data.get("data", {}).get("reply_list", [])
            print(f"\n===== 收到 {len(replies)} 条新回复 =====")
            for item in replies:
                print(f"👤 {item.get('author_name')} 在《{item.get('title')[:10]}...》中说：")
                print(f"💬 {item.get('content')}")
                print(f"🔗 https://tieba.baidu.com/p/{item.get('thread_id')} (post_id: {item.get('post_id')})")
                print("-" * 40)
        else:
            print(f"❌ 查询失败: {res_data.get('error')}")
    except Exception as e:
        print(f"⚠️ 程序出错: {e}")

def reply_post(tid, pid, content):
    # 修正：将参数转为 int
    payload = {"thread_id": int(tid), "content": content}
    if int(pid) != 0:
        payload["post_id"] = int(pid)

    try:
        response = requests.post(data.reply_URL, json=payload, headers=headers)
        res_data = response.json()
        if res_data.get("errno") == 0:
            new_pid = res_data.get("data", {}).get("post_id")
            print(f"✅ 回复成功！内容: {content}")
            print(f"🔗 https://tieba.baidu.com/p/{tid}?pid={new_pid}")
        else:
            print(f"❌ 失败: {res_data.get('errmsg')}")
    except Exception as e:
        print(f"⚠️ 出错: {e}")

def main():
    args = sys.argv
    if len(args) < 2:
        print("用法: python3 tieba.py [create_thread | check_reply | reply]")
        return

    req_type = args[1]
    # 修正：match 语句每个 case 后需要冒号
    match req_type:
        case "create_thread":
            if len(args) == 4:
                create_thread(args[2], args[3])
            else:
                print("用法: python3 tieba.py create_thread <标题> <内容>")

        case "check_reply":
            check_reply()

        case "reply":
            if len(args) == 5:
                # args[2]=tid, args[3]=pid, args[4]=content
                reply_post(args[2], args[3], args[4])
            else:
                print("用法: python3 tieba.py reply <tid> <pid_or_0> <内容>")
        case _:
            print("未知指令")

if __name__ == "__main__":
    main()