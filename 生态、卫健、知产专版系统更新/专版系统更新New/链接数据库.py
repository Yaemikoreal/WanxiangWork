# coding:utf-8
import pyodbc

"""
    链接信息:
        作用： 用于返回数据库链接信息
        参数：
            targetSource: 数据库方向(自己、服务器、公司[自己电脑])
"""


def sql_server_info(targetSource="服务器"):
    # 本地 自己 或者 服务器
    if targetSource == "自己":
        connInfo = 'DRIVER={SQL Server};SERVER=localhost;DATABASE=自收录数据;UID=sa;PWD=123456'
    elif targetSource == "公司":
        connInfo = 'DRIVER={SQL Server};SERVER=192.168.31.112;DATABASE=自收录数据;UID=sa;PWD=123456'
        # Target_table_name = "[xb].dbo.[疫情]"  # 合同范本 -补充
    elif targetSource == "服务器":
        # DRIVER={SQL Server};SERVER=SC-201704181448\\SQLEXPRESS;DATABASE=[cnlaw1.0];UID=sa;PWD=123qwe!@#
        # connInfo = 'DRIVER={SQL Server};SERVER=192.168.31.124\SQLEXPRESS;DATABASE=自收录数据;UID=sa;PWD=123qwe!@#'
        connInfo ='DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#'
        # connInfo = 'DRIVER={SQL Server};SERVER=SC-201704181448\SQLEXPRESS;DATABASE=自收录数据;UID=sa;PWD=123qwe!@#'

    elif targetSource == "法宝6.0":
        # DRIVER={SQL Server};SERVER=SC-201704181448\\SQLEXPRESS;DATABASE=[cnlaw1.0];UID=sa;PWD=123qwe!@#
        # connInfo = 'DRIVER={SQL Server};SERVER=192.168.31.124\SQLEXPRESS;DATABASE=自收录数据;UID=sa;PWD=123qwe!@#'
        connInfo = 'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=FB6.0;UID=saa;PWD=1+2-3..*Qwe!@#'
        # connInfo = 'DRIVER={SQL Server};SERVER=SC-201704181448\SQLEXPRESS;DATABASE=自收录数据;UID=sa;PWD=123qwe!@#'
    elif targetSource == "法宝5.0":
        # DRIVER={SQL Server};SERVER=SC-201704181448\\SQLEXPRESS;DATABASE=[cnlaw1.0];UID=sa;PWD=123qwe!@#
        # connInfo = 'DRIVER={SQL Server};SERVER=192.168.31.124\SQLEXPRESS;DATABASE=自收录数据;UID=sa;PWD=123qwe!@#'
        connInfo = 'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=FddLaw5.0;UID=saa;PWD=1+2-3..*Qwe!@#'
        # connInfo = 'DRIVER={SQL Server};SERVER=SC-201704181448\SQLEXPRESS;DATABASE=自收录数据;UID=sa;PWD=123qwe!@#'

    else:
        raise Exception("目标数据库错误")
    return connInfo


def get_connect_cursor(connInfo):
    conn = pyodbc.connect(connInfo)
    # conn = pyodbc.connect('DRIVER={SQL Server};SERVER=192.168.31.124\SQLEXPRESS;DATABASE=cnlaw2.0;UID=sa;PWD=123qwe!@#')
    # 打开游标
    cursor = conn.cursor()
    if not cursor:
        raise Exception('数据库连接失败！')


    # 返回一个连接(conn)用于关闭，返回一个游标(cursor)，
    return conn, cursor


def query(cursor, sql):
    cursor.execute(sql)
    row = cursor.fetchone()
    # 在查询的的时候使用：cursor.fetchone()返回一个元组的结果集， 没有结果的时候 返回 None
    # 返回一个row（查询的结果集）,注意使用完查询后，记得使用关闭方法

    return row


def query_1(cursor, sql):
    cursor.execute(sql)
    row = cursor.fetchall()

    # 在查询的的时候使用：cursor.fetchone()返回一个元组的结果集, ，没结果的时候返回 一个空列表
    # 在插入的时候直接传入一个sql语句就行了不用使用后面的语句 ： cursor.execute("insert into tableName( , ) values ('', ' ')")
    #                    conn.commit()
    # 返回一个rows（查询的结果集）,注意使用完查询后，记得使用关闭方法

    return row


def insert(cursor, sql):
    cursor.execute(sql)


def insert_1(conn, cursor, sql):
    cursor.execute(sql)
    conn.commit()


def insert_(conn_info, sql):
    conn_cur = get_connect_cursor(conn_info)
    conn = conn_cur[0]
    cur = conn_cur[1]
    # print(sql)
    # input()
    insert(cur, sql)
    conn.commit()
    conn.close()

def query_del(conn_info, sql):
    conn_cur = get_connect_cursor(conn_info)
    conn = conn_cur[0]
    cur = conn_cur[1]
    # print(sql)
    # input()
    cur.execute(sql)
    conn.commit()
    conn.close()

def break_connect(conn):
    conn.commit()
    conn.close()
    print("数据库链接已关闭")


#
# connect_cursor = get_connect_cursor()
# connect = connect_cursor[0]
# cursor = connect_cursor[1]
# sql_1 = "select *  from [自收录数据].dbo.[AdministrativeCase-行政执法案例] where 标题='周根年遮挡船名案' and 文号='浙'"
# ss = query(cursor , sql_1)
#
# print(ss)
# if ss is None:
#     print("yes")
# print(type(ss))


# 测试用的，需要才打开下面的注释
# if __name__ == '__main__':
#     conninfo = sql_server_info()
#     print(conninfo)
#     connInfo = sql_server_info("服务器")
#     connect_cursor = get_connect_cursor(connInfo)
#     connect = connect_cursor[0]
#     cursor = connect_cursor[1]
#     qu_sql = "SELECT * FROM  [自收录数据].[dbo].[hb-环保局] where  标题='加强衔接配合，强化内外监督，重拳打击环境犯罪 ——环境保护部转发最高检《全国检察机关开展“破坏环境资源犯罪专项立案监督活动”和“危害食品药品安全犯罪专项立案监督活动”的工作方案》解读'"
#     in_sql = ""
#     # insert_(connInfo, in_sql)
#     qu_rs = query(cursor, qu_sql)
#     print(qu_rs)
#     if qu_rs != None:
#         print("ss")
#     else:
#         print(qu_rs)

