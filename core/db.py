# -*- coding: utf-8 -*-
import pymysql

class DBManager:
    @staticmethod
    def test_conn(host, port, user, pwd, dbname=""):
        """测试数据库连接"""
        try:
            conn = pymysql.connect(
                host=host,
                port=int(port),
                user=user,
                password=pwd,
                database=dbname,
                charset="utf8mb4",
                connect_timeout=5
            )
            conn.close()
            return True, "数据库连接成功！"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def exec_sql(host, port, user, pwd, dbname, sql):
        """执行SQL语句"""
        try:
            conn = pymysql.connect(
                host=host,
                port=int(port),
                user=user,
                password=pwd,
                database=dbname,
                charset="utf8mb4"
            )
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql)

            # 判断SQL类型：查询返回结果，增删改返回影响行数
            if sql.strip().upper().startswith(("SELECT", "SHOW", "DESC")):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = f"执行成功，影响行数：{cursor.rowcount}"

            conn.close()
            return True, result
        except Exception as e:
            return False, str(e)