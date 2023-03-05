import smtplib
from email.mime.text import MIMEText
from kubernetes import client, config
import time

# 配置 K8s API 客户端
config.load_kube_config()
v1 = client.CoreV1Api()

# 邮件通知配置
smtp_server = 'smtp.example.com'
smtp_port = 587
smtp_user = 'user@example.com'
smtp_password = 'password'
mail_from = 'user@example.com'
mail_to = ['user1@example.com', 'user2@example.com']
mail_subject = 'K8s Pod 监控告警'

# 监控循环
while True:
    # 获取所有运行中的 Pod
    pods = v1.list_pod_for_all_namespaces(watch=False)
    # 统计运行中和失败的 Pod 数量
    running_pods = 0
    failed_pods = 0
    for pod in pods.items:
        if pod.status.phase == 'Running':
            running_pods += 1
        elif pod.status.phase == 'Failed':
            failed_pods += 1
    
    # 发送邮件通知
    if failed_pods > 0:
        mail_body = f"当前共有 {running_pods+failed_pods} 个 Pod，其中 {failed_pods} 个 Pod 处于失败状态。"
        msg = MIMEText(mail_body)
        msg['From'] = mail_from
        msg['To'] = ', '.join(mail_to)
        msg['Subject'] = mail_subject
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.sendmail(mail_from, mail_to, msg.as_string())
        smtp.quit()
    
    # 等待 5 分钟后再次检查
    time.sleep(300)
