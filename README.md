# QingLong-MyScripts

统一管理夸克网盘、WorkBuddy 国内版和中国移动云盘。青龙只订阅本仓库；每 6 小时自动检查三个上游。个人免费使用，非官方项目，保留原作者、MIT 许可证和转载声明。

## 仓库结构

    QingLong-MyScripts/
    ├── WorkBuddy/
    │   ├── workbuddy_daily.py
    │   └── workbuddy_login.py
    ├── Quark/
    │   └── quark.py
    ├── ChinaMobile/              中国移动云盘及三个同目录辅助模块
    ├── README.md
    ├── requirements.txt
    ├── licenses/                 原作者许可证
    ├── upstream/                 原作者说明、声明及来源校验记录
    ├── sync_upstream.py          源码同步工具，不加入青龙定时任务
    └── .github/workflows/sync.yml

## 第一步：添加一个青龙订阅

订阅管理 → 新建：

| 字段 | 内容 |
| --- | --- |
| 名称 | QingLong-MyScripts |
| 类型 | 公开仓库 |
| 链接 | https://github.com/caozzzzz/QingLong-MyScripts.git |
| 分支 | main |
| 定时规则 | 45 */6 * * * |
| 文件后缀 | py |
| 黑名单、执行前、执行后 | 留空 |
| 自动添加任务、自动删除任务 | 关闭 |

白名单（匹配子目录中的三个运行脚本）：

    (^|/)(quark|workbuddy_daily|中国移动云盘)\.py$

依赖文件（登录工具和移动云盘辅助模块，不为它们创建定时任务）：

    (^|/)(workbuddy_login|log|get_env|sendNotify)\.py$

保存后运行订阅。只需订阅这一个仓库，不用再单独添加上游。

## 第二步：安装依赖

依赖管理 → Python3 → 新建，安装 requests、httpx、python-dotenv，等待成功。

## 第三步：填写账号环境变量

- QUARK_COOKIE：kps=实际值; sign=实际值; vcode=实际值#备注。需要夸克移动端参数，多账号每行一个。获取步骤见[夸克原作者说明](https://github.com/GGBondHere/QingLongScripts/blob/main/docs/quark.md)。
- WORKBUDDY_REFRESH_TOKEN：手机号:AT:RT，多账号每行一个。没有令牌时，可下载 WorkBuddy/workbuddy_login.py 到本地交互登录，详见[WorkBuddy 原作者说明](https://github.com/L0NE-6/WorkBuddy-Daily#readme)。
- 推荐 WORKBUDDY_STATE_DIR：设置独立持久化目录，例如 /ql/data/workbuddy-state，先确保目录已创建且可写，保留轮换令牌。已运行过旧路径脚本时，先迁移其令牌状态文件或重新登录，再切换新路径。

凭证仅填写青龙，不提交本公开仓库。本仓库 Actions 只同步源码，不运行签到，也不需要账号 Secrets。

## 第四步：创建并试运行定时任务

从青龙脚本列表选择实际路径；下表目录名为示例，以面板实际拉取目录为准，保留 WorkBuddy/ 和 Quark/ 层级。时区使用 Asia/Shanghai。

| 任务 | 命令示例 | 北京时间定时 |
| --- | --- | --- |
| 夸克签到 | task caozzzzz_QingLong-MyScripts_main/Quark/quark.py | 15 8 * * * |
| WorkBuddy 日常 | task caozzzzz_QingLong-MyScripts_main/WorkBuddy/workbuddy_daily.py | 17 7,12 * * * |
| WorkBuddy 夜间 | 同上 | 37 23 * * * |

先分别手动运行夸克和 WorkBuddy 日常任务，核对日志，再保留定时执行。workbuddy_login.py 为交互登录工具，不创建定时任务。

若之前已添加旧版根目录任务，切换前停用旧任务，避免重复运行。青龙内实际目录以订阅日志、脚本管理为准。

夸克使用青龙面板通知；WorkBuddy 新版青龙默认通知可能需要 QL_CLIENT_ID、QL_CLIENT_SECRET 与 system 权限，详见上游说明。

## 自动同步与来源

Actions → Sync selected upstream scripts → Run workflow 可手动更新。GitHub 定时可能延迟，公开仓库长期无活动时可能停用定时，需要手动重新启用。

- [GGBondHere/QingLongScripts](https://github.com/GGBondHere/QingLongScripts)：仅 scripts/quark.py，另保留夸克说明与 MIT 许可证，不同步其他平台。
- [L0NE-6/WorkBuddy-Daily](https://github.com/L0NE-6/WorkBuddy-Daily)：国内版 workbuddy_daily.py、workbuddy_login.py，另保留 MIT 许可证与 NOTICE，不同步国际版及上游签到工作流。

upstream/manifest.json 记录来源提交与文件 SHA256。请遵守平台规则和 upstream/WorkBuddy-NOTICE.md，不用于收费包装、引流或冒充作者。


## 中国移动云盘

已同步到 ChinaMobile/，包含中国移动云盘.py、log.py、get_env.py、sendNotify.py，必须同目录。来源：[LeonByte/QL_TimingScript](https://gitee.com/liu-long068/QL_TimingScript)。原仓库未指定许可证，完整使用声明保留在 upstream/QL_TimingScript-README.md，不对这些文件另行授予 MIT 许可。

配置 ydyp_ck、ydyp_ua 和建议的 ydyp_device_token 后，先带 --check 参数自检，再正常运行。移动脚本还包括任务、上传及活动巡检等上游流程；通知使用配套 sendNotify.py 的渠道配置。

完整步骤见 [ChinaMobile/README.md](ChinaMobile/README.md)。示例任务：

    task caozzzzz_QingLong-MyScripts_main/ChinaMobile/中国移动云盘.py

示例定时：0 8,10,12,15 * * *。不要给 log.py、get_env.py、sendNotify.py 创建定时任务。
