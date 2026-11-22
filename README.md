# 我的青龙脚本订阅

只同步夸克网盘和 WorkBuddy 国内版，个人免费使用。保留原作者、MIT 许可证及 NOTICE，非官方项目。

## 青龙订阅

| 字段 | 填写内容 |
| --- | --- |
| 名称 | QingLong-MyScripts |
| 类型 | 公开仓库 |
| 链接 | https://github.com/caozzzzz/QingLong-MyScripts.git |
| 分支 | main |
| 定时规则 | 45 */6 * * * |
| 文件后缀 | py |
| 黑名单、依赖文件、执行前、执行后 | 留空 |
| 自动添加任务、自动删除任务 | 关闭 |

白名单填写下面这一行，只拉取两项运行脚本：

    ^(quark|workbuddy_daily)\.py$

Python3 依赖安装 requests。运行订阅后手动创建定时任务，从脚本列表选择实际路径。下面目录是示例，以面板实际路径为准；时区设为 Asia/Shanghai。

| 任务 | 命令示例 | 北京时间定时 |
| --- | --- | --- |
| 夸克签到 | task caozzzzz_QingLong-MyScripts_main/quark.py | 15 8 * * * |
| WorkBuddy 日常 | task caozzzzz_QingLong-MyScripts_main/workbuddy_daily.py | 17 7,12 * * * |
| WorkBuddy 夜间 | 同上 | 37 23 * * * |

不要将 sync_upstream.py 或 workbuddy_login.py 加入签到定时任务。

## 环境变量

- QUARK_COOKIE：kps=实际值; sign=实际值; vcode=实际值#备注。需要移动端参数，多账号每行一个。
- WORKBUDDY_REFRESH_TOKEN：手机号:AT:RT，多账号每行一个。
- 建议 WORKBUDDY_STATE_DIR 指向独立持久化目录，例如 /ql/data/workbuddy-state，先确认目录已创建且可写，以保留轮换令牌。

账号凭证只填青龙，不提交到本公开仓库。本仓库 GitHub Actions 只同步源码，不执行签到，也不需要账号 Secrets。

夸克使用面板通知。WorkBuddy 新版青龙通知可能需要 QL_CLIENT_ID、QL_CLIENT_SECRET 及 system 权限，详见上游说明。

## 自动同步和来源

每 6 小时由 GitHub Actions 检查上游。可在 Actions → Sync selected upstream scripts → Run workflow 手动同步。定时可能延迟，公开仓库长期无活动时可能停用定时，需要手动重新启用。

- [GGBondHere/QingLongScripts](https://github.com/GGBondHere/QingLongScripts)：仅 scripts/quark.py；另保留夸克说明和 MIT 许可证，不包含其他服务。
- [L0NE-6/WorkBuddy-Daily](https://github.com/L0NE-6/WorkBuddy-Daily)：国内版 workbuddy_daily.py、交互登录工具 workbuddy_login.py；另保留 MIT 许可证和 NOTICE，不包含国际版或上游签到工作流。

凭证获取方法：[夸克说明](https://github.com/GGBondHere/QingLongScripts/blob/main/docs/quark.md)、[WorkBuddy 说明](https://github.com/L0NE-6/WorkBuddy-Daily#readme)。

upstream/manifest.json 记录精确来源提交和文件 SHA256。遵守平台规则及 upstream/WorkBuddy-NOTICE.md，不用于收费包装、引流或冒充作者。
