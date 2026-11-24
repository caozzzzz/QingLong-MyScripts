# QingLong-MyScripts

一个青龙订阅管理夸克、WorkBuddy 国内版和中国移动云盘，三者共用 common/notify.py，每 6 小时检查上游。

## 目录

    common/notify.py                 唯一公共 Bark 发送模块
    Quark/quark.py
    WorkBuddy/workbuddy_daily.py
    WorkBuddy/workbuddy_login.py      交互登录工具
    ChinaMobile/中国移动云盘.py
    ChinaMobile/log.py                日志收集
    ChinaMobile/get_env.py            环境变量读取
    licenses/                        原作者许可证
    upstream/                        声明、说明、来源校验

## 青龙订阅及升级

公开仓库链接：https://github.com/caozzzzz/QingLong-MyScripts.git

分支 main，订阅定时 45 */6 * * *，文件后缀 py，黑名单、执行前、执行后留空，自动添加任务和自动删除任务关闭。

白名单：

    Quark/|WorkBuddy/workbuddy_daily|ChinaMobile/

依赖文件（必须更新，保证拉取公共模块）：

    (^|/)(common/notify|workbuddy_login|log|get_env)\.py$

先保存依赖设置，再运行订阅。完成后在同一订阅目录下确认 common/notify.py 存在，再运行业务任务。不要在更新过程中运行任务。

原任务命令、账号变量、BARK、定时均不变，无需新建通知任务。Python3 依赖保持 requests、httpx、python-dotenv。公共模块按脚本文件路径加载，不依赖启动目录，不会误用根目录同名 notify.py。

新版已移除 ChinaMobile/sendNotify.py，移动云盘不再导入它；青龙本地如有旧文件残留也不会调用。青龙自动提供或其他订阅依赖的 notify.py、sendNotify.js 保留，不要批量删除。

## 公共 Bark 通知

三个脚本统一调用 common/notify.py。配置优先级：BARK（官方设备 Key）→ BARK_URL → BARK_PUSH（完整服务器/设备 Key 地址），已有 BARK 可直接复用。凭证只填青龙，不提交公开仓库。

正文要求保存到 Bark 历史，分别使用“夸克网盘”“WorkBuddy”“移动云盘”分组。优先完整发一条，仅服务器明确返回消息过大时分段；超时等结果不确定的失败不自动重发。旧消息不补存。

配置直接 Bark 后，WorkBuddy 和夸克不重复走青龙面板通知；未配置时保留其原面板渠道，移动云盘也尝试运行环境提供的 QLAPI。移动云盘旧 sendNotify.py 的其他通知渠道变量不再读取；WorkBuddy 独立配置的其他非 Bark 渠道仍保留。

## 任务与账号

面板时区 Asia/Shanghai，命令中订阅目录以脚本管理实际路径为准。

| 服务 | 命令示例 | 北京时间定时 |
| --- | --- | --- |
| 夸克 | task caozzzzz_QingLong-MyScripts_main/Quark/quark.py | 15 8 * * * |
| WorkBuddy | task caozzzzz_QingLong-MyScripts_main/WorkBuddy/workbuddy_daily.py | 17 7,12 * * * |
| WorkBuddy 夜间 | 同上 | 37 23 * * * |
| 移动云盘 | task caozzzzz_QingLong-MyScripts_main/ChinaMobile/中国移动云盘.py | 0 8,10,12,15 * * * |

- QUARK_COOKIE：kps=实际值; sign=实际值; vcode=实际值，多账号换行。
- WORKBUDDY_REFRESH_TOKEN：手机号:AT:RT，多账号换行。建议 WORKBUDDY_STATE_DIR 指向独立持久化可写目录保存轮换令牌。
- 移动云盘：详见 [ChinaMobile/README.md](ChinaMobile/README.md)，首次可在命令末尾加 --check 自检。

## 来源和维护

- [GGBondHere/QingLongScripts](https://github.com/GGBondHere/QingLongScripts)：只收录夸克，保留 MIT 许可证。
- [L0NE-6/WorkBuddy-Daily](https://github.com/L0NE-6/WorkBuddy-Daily)：国内版与登录工具，保留 MIT 许可证及 NOTICE。
- [LeonByte/QL_TimingScript](https://gitee.com/liu-long068/QL_TimingScript)：移动云盘、log.py、get_env.py，未指定许可证，完整声明保留在 upstream/QL_TimingScript-README.md，不为这些文件另行授予 MIT 许可。

仅适配通知接入，其余业务沿用上游；移动云盘包括任务、上传与活动巡检，不仅签到。upstream/manifest.json 记录来源提交、原始及适配后 SHA256。

Actions 可手动运行同步；定时可能延迟，长期无活动可能需重新启用。每次同步重新应用公共通知接入，并运行无账号、无真实推送的模拟测试。请遵守平台及原作者声明，不用于收费包装或引流。
