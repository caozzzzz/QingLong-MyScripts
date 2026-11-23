# 中国移动云盘

来源：[LeonByte / QL_TimingScript](https://gitee.com/liu-long068/QL_TimingScript)，主脚本作者标注为 Echo。原样同步中国移动云盘.py、log.py、get_env.py、sendNotify.py，四个 Python 文件必须同目录，不同步其他业务脚本或抓包工具。

原仓库未标注开源许可证；其 README 含非商业、学习测试等使用声明，完整保留在 [原作者说明](../upstream/QL_TimingScript-README.md)。本合集不为这些文件另行授予 MIT 许可，请遵守原作者声明。

## 青龙设置

Python3 依赖：httpx、python-dotenv、requests。

在同一个 QingLong-MyScripts 订阅内，白名单改为：

    (^|/)(quark|workbuddy_daily|中国移动云盘)\.py$

依赖文件改为：

    (^|/)(workbuddy_login|log|get_env|sendNotify)\.py$

自动添加任务、自动删除任务均关闭。保存后运行订阅，确认四个 Python 文件在 ChinaMobile/ 同级目录中。不要为三个辅助模块创建定时任务。

## 环境变量

| 名称 | 内容 |
| --- | --- |
| ydyp_ck | 必填：authorization#手机号，authorization 保留 Basic 前缀；完整支持 authorization#手机号#jwtToken#deviceId，多账号用 @ 分隔 |
| ydyp_ua | 必填：自己手机的完整 User-Agent，与自己的设备对应 |
| ydyp_device_token | 强烈建议：App 领取请求 receiveV3 请求体中的 deviceId 整串；缺失可能导致签到、领豆返回 614 |
| ydyp_device_id | 可选：UUID 设备号，与上面的设备令牌不同 |
| ydyp_upload_fill | 可选：保持默认 0 |

凭证只填写青龙，勿提交公开仓库或发送未脱敏日志。获取细节见主脚本开头注释或原作者说明。

## 首次运行

从脚本列表选择实际路径。先以自检命令运行一次：

    task caozzzzz_QingLong-MyScripts_main/ChinaMobile/中国移动云盘.py --check

确认凭据与状态正常后，改为正常命令：

    task caozzzzz_QingLong-MyScripts_main/ChinaMobile/中国移动云盘.py

示例定时（北京时间）：0 8,10,12,15 * * *。目录名以青龙实际拉取路径为准。

该上游脚本包含签到、任务、领豆、上传文件和活动巡检等流程，并非仅签到；本合集保持上游行为，未使用账号执行验证。通知由配套 sendNotify.py 读取相应渠道环境变量，不应假定自动沿用青龙面板通知设置。
