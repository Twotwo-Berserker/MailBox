import pymysql
from datetime import datetime, timedelta

# 数据库连接信息（与server.py保持一致）
def get_conn():
    return pymysql.connect(
        host='Oneone22.mysql.pythonanywhere-services.com',
        user='Oneone22',
        password='160384Az',
        db='Oneone22$maibox',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def delete_old_messages():
    # 计算三天前的时间
    three_days_ago = datetime.now() - timedelta(days=3)

    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            # 删除三天前的消息
            cursor.execute(
                "DELETE FROM messages WHERE timestamp < %s",
                (three_days_ago,)
            )
            conn.commit()
            print(f"Deleted {cursor.rowcount} old messages")
    finally:
        conn.close()

if __name__ == "__main__":
    delete_old_messages()