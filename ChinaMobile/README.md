# 中国移动云盘

来源：[LeonByte/QL_TimingScript](https://gitee.com/liu-long068/QL_TimingScript)，作者标注 Echo。保留主脚本、log.py、get_env.py；通知改为 ../common/notify.py，不再依赖 sendNotify.py。

原作者未指定许可证，完整声明见 [原作者说明](../upstream/QL_TimingScript-README.md)，不为其另行授予 MIT 许可。

青龙订阅公共模块依赖配置见[总说明](../README.md)。Python3 依赖：requests、httpx、python-dotenv。

| 环境变量 | 内容 |
| --- | --- |
| ydyp_ck | 必填：authorization#手机号，保留 Basic 前缀；完整支持 authorization#手机号#jwtToken#deviceId，多账号用 @ 分隔 |
| ydyp_ua | 必填：自己手机完整 User-Agent |
| ydyp_device_token | 强烈建议：receiveV3 领取请求体里的 deviceId 整串，与 UUID 设备号不同 |
| ydyp_device_id | 可选：UUID 设备号 |
| ydyp_upload_fill | 保持默认 0 |
| BARK | 官方 Bark 设备 Key，已有变量不必重建 |

凭证获取细节见脚本头部原作者注释，凭证只填青龙，不上传仓库。

自检命令（目录以面板为准）：

    task caozzzzz_QingLong-MyScripts_main/ChinaMobile/中国移动云盘.py --check

自检通过后去掉 --check，示例定时：0 8,10,12,15 * * *。log.py、get_env.py、common/notify.py 不建定时任务。

通知由公共模块发送并要求保存到“移动云盘”分组。不再读取旧 sendNotify.py 的其他通知渠道变量；未配置 Bark 时尝试 QLAPI 面板通知。业务仍包括签到、任务、上传和活动巡检，沿用上游行为。
