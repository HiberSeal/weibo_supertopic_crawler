# wbsupertopic_crawler

新浪微博超级话题内微博相关数据爬取，一个特别简单的程序，就一个python文件crawler.py。

**一句话简介**

将指定超话内的微博爬取并存入Mysql数据库。

| 运行环境 | 版本号 |
| :------: | :----: |
|  Python  |  3.8   |
|  Mysql   | 5.7.14 |

**使用说明**

HTTP GET请求headers里的**Referer**，params里的**extparam**、**containerid**，换上指定超话h5页面中的值即可。

**存在问题**

第一次写python，遇到了很多问题：

1. 不能爬取到整个超话所有的微博，1.2万的总微博数大概能爬取到9千多条。

   直接原因应该是请求的接口返回的数据量不稳定，正常情况下应该是每请求一次返回10条数据，但是运行一会儿就会间断性出现不足10条的情况。以及感觉是没有返回到最终数据的页码（since_id）的。

2. 执行一段时间会自己停掉，也不报错，最多一次坚持到爬取了3800多条数据，比较影响使用体验。

3. 存在过爬取了1千多条数据（爬取超话的微博总数是1.2万）之后，不返回下一页页码（since_id），过了几个小时之后请求相同的接口，又返回下一页页码（since_id）了。


希望有大佬不吝啬指教，帮助解决上面的问题！

<br>

**DDL**

也在这里记录下数据表的DDL

```sql
CREATE TABLE `rosemin`.`wbsupertopic`  (
  `post_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '发布时间',
  `poster` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '发布人',
  `region` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '地区',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '内容',
  `reposts_count` int(255) NULL DEFAULT NULL COMMENT '转发数',
  `comments_count` int(255) NULL DEFAULT NULL COMMENT '评论数',
  `attitudes_count` int(255) NULL DEFAULT NULL COMMENT '点赞数',
  `weibo_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '微博地址',
  `create_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '入库时间',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`weibo_url`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '微博超话爬取' ROW_FORMAT = DYNAMIC;
```
